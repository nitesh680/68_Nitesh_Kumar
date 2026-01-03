import csv
import io
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
    data = await file.read()
    try:
        df = pd.read_csv(io.BytesIO(data))
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid CSV") from e

    required = {"date", "amount", "description"}
    if not required.issubset(set(df.columns)):
        raise HTTPException(status_code=400, detail=f"CSV must contain columns: {sorted(required)}")

    if df["description"].isna().all():
        raise HTTPException(status_code=400, detail="CSV description column is empty")

    inserted = 0
    for _, row in df.iterrows():
        try:
            dt = pd.to_datetime(row["date"], utc=True).to_pydatetime()
        except Exception:
            continue

        desc = str(row.get("description") or "").strip()
        if not desc:
            continue
        amt = float(row.get("amount") or 0.0)

        try:
            result = await categorize(desc)
        except Exception as e:
            # Fallback: categorize with default if categorizer fails
            from app.services.categorizer import CategorizeResult
            result = CategorizeResult(
                category="Other",
                confidence=0.25,
                source="fallback",
                explanation=f"Categorization failed: {str(e)[:100]}"
            )

        tx_id = str(uuid4())
        doc = {
            "_id": tx_id,
            "user_id": user["_id"],
            "date": dt,
            "description": desc,
            "amount": amt,
            "category": result.category,
            "confidence": result.confidence,
            "source": result.source,
            "explanation": result.explanation,
            "created_at": datetime.utcnow(),
        }
        await db.transactions.insert_one(doc)
        inserted += 1

    return TransactionUploadResponse(inserted=inserted)


@router.get("/month/{month}", response_model=MonthSummary)
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
