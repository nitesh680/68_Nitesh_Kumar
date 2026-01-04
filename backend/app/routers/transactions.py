from datetime import datetime
from uuid import uuid4

import pandas as pd
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.deps import get_current_user
from app.db.mongo import get_db
from app.schemas.transactions import (
    CategorizeResponse,
    MonthSummary,
    TransactionCreate,
    TransactionOut,
    TransactionUploadResponse,
)
from app.services.categorizer import categorize

router = APIRouter()


@router.post("/", response_model=TransactionOut)
async def create_transaction(payload: TransactionCreate, user=Depends(get_current_user), db=Depends(get_db)):
    result = await categorize(payload.description)
    tx_id = str(uuid4())
    doc = {
        "_id": tx_id,
        "user_id": user["_id"],
        "date": payload.date,
        "description": payload.description,
        "amount": float(payload.amount),
        "category": result.category,
        "confidence": result.confidence,
        "source": result.source,
        "explanation": result.explanation,
        "created_at": datetime.utcnow(),
    }
    await db.transactions.insert_one(doc)
    return TransactionOut(
        id=tx_id,
        date=doc["date"],
        description=doc["description"],
        amount=doc["amount"],
        category=doc["category"],
        confidence=doc["confidence"],
        source=doc["source"],
        explanation=doc["explanation"],
    )


@router.get("/recent", response_model=list[TransactionOut])
async def recent(limit: int = 20, user=Depends(get_current_user), db=Depends(get_db)):
    cursor = db.transactions.find({"user_id": user["_id"]}).sort("date", -1).limit(limit)
    out: list[TransactionOut] = []
    async for doc in cursor:
        out.append(
            TransactionOut(
                id=doc["_id"],
                date=doc["date"],
                description=doc["description"],
                amount=doc["amount"],
                category=doc.get("category"),
                confidence=doc.get("confidence"),
                source=doc.get("source"),
                explanation=doc.get("explanation"),
            )
        )
    return out


@router.post("/categorize", response_model=CategorizeResponse)
async def categorize_only(description: str, user=Depends(get_current_user)):
    result = await categorize(description)
    return CategorizeResponse(
        category=result.category,
        confidence=result.confidence,
        source=result.source,
        explanation=result.explanation,
    )


@router.post("/upload", response_model=TransactionUploadResponse)
async def upload_csv(file: UploadFile = File(...), user=Depends(get_current_user), db=Depends(get_db)):
    print(f"Upload request from user: {user['_id']}")
    try:
        contents = await file.read()

        import io

        df = pd.read_csv(io.StringIO(contents.decode("utf-8")))
        print(f"CSV parsed with {len(df)} rows")
        print(f"Columns: {list(df.columns)}")

        # Find required columns (case insensitive)
        required_cols = {'date', 'amount', 'description'}
        actual_cols = {str(col).strip().lower() for col in df.columns}
        
        missing_cols = required_cols - actual_cols
        if missing_cols:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_cols)}. Found: {', '.join(actual_cols)}"
            )

        inserted = 0
        months: list[str] = []
        for _, row in df.iterrows():
            # Get description for categorization
            desc = str(row.get('description', '')).strip()
            if not desc:
                continue

            # Find the amount column (case insensitive)
            amt = None
            for col in df.columns:
                if str(col).strip().lower() == "amount":
                    amt = float(row[col] or 0.0)
                    break
            if amt is None or amt == 0.0:
                continue

            # Parse and normalize the date
            date_val = row.get("date", "")
            if pd.isna(date_val) or not date_val:
                continue

            parsed_ts = pd.to_datetime(date_val, utc=True, errors="coerce")
            if pd.isna(parsed_ts):
                continue

            parsed_date = parsed_ts.to_pydatetime()
            # Store as naive UTC so month filtering with naive datetimes works reliably
            if getattr(parsed_date, "tzinfo", None) is not None:
                parsed_date = parsed_date.replace(tzinfo=None)

            months.append(parsed_date.strftime("%Y-%m"))

            try:
                # Use a timeout for categorization to prevent delays
                import asyncio
                result = await asyncio.wait_for(categorize(desc), timeout=2.0)
            except asyncio.TimeoutError:
                # Fallback if categorization takes too long
                from app.services.categorizer import CategorizeResult
                result = CategorizeResult(
                    category="Other",
                    confidence=0.25,
                    source="timeout",
                    explanation="Categorization timed out"
                )
            except Exception as e:
                # Fallback: categorize with default if categorizer fails
                from app.services.categorizer import CategorizeResult
                result = CategorizeResult(
                    category="Other",
                    confidence=0.25,
                    source="fallback",
                    explanation=f"Categorization failed: {str(e)[:100]}"
                )

            # Store in MongoDB with user association
            doc = {
                "_id": str(uuid4()),
                "user_id": user["_id"],
                "date": parsed_date,
                "description": desc,
                "amount": amt,
                "category": result.category,
                "confidence": result.confidence,
                "source": result.source,
                "explanation": result.explanation,
                "created_at": datetime.utcnow(),
            }
            result = await db.transactions.insert_one(doc)
            inserted += 1

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Upload failed: {e}")

    uniq_months = sorted(set(months))
    min_month = uniq_months[0] if uniq_months else None
    max_month = uniq_months[-1] if uniq_months else None

    print(f"Total inserted: {inserted} transactions")
    return TransactionUploadResponse(inserted=inserted, min_month=min_month, max_month=max_month, latest_month=max_month)


@router.get("/month-summary/{month}", response_model=MonthSummary)
async def month_summary(month: str, user=Depends(get_current_user), db=Depends(get_db)):
    if len(month) != 7 or month[4] != "-":
        raise HTTPException(status_code=400, detail="Month must be YYYY-MM")

    start = datetime.fromisoformat(month + "-01")
    if month[5:7] == "12":
        end = datetime.fromisoformat(str(int(month[:4]) + 1) + "-01-01")
    else:
        end = datetime.fromisoformat(month[:5] + f"{int(month[5:7]) + 1:02d}" + "-01")

    pipeline = [
        {
            "$match": {
                "user_id": user["_id"],
                "date": {"$gte": start, "$lt": end},
            }
        },
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
    ]

    by_category = {}
    total = 0.0
    async for row in db.transactions.aggregate(pipeline):
        cat = row.get("_id") or "Other"
        val = float(row.get("total") or 0.0)
        by_category[cat] = val
        total += val

    return MonthSummary(month=month, total_spend=total, by_category=by_category)
