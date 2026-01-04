from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.deps import get_current_user
from app.db.mongo import get_db
from app.schemas.analytics import AnomalyPoint, DashboardSummary, TrendPoint

router = APIRouter()


@router.get("/dashboard", response_model=DashboardSummary)
async def dashboard(month: str, user=Depends(get_current_user), db=Depends(get_db)):
    if len(month) != 7 or month[4] != "-":
        raise HTTPException(status_code=400, detail="Month must be YYYY-MM")

    start = datetime.fromisoformat(month + "-01")
    if month[5:7] == "12":
        end = datetime.fromisoformat(str(int(month[:4]) + 1) + "-01-01")
    else:
        end = datetime.fromisoformat(month[:5] + f"{int(month[5:7]) + 1:02d}" + "-01")

    print(f"Dashboard request for user: {user['_id']}, month: {month}")
    print(f"Date range: {start} to {end}")

    # Use aggregation for better performance - get all metrics in one query
    pipeline = [
        {"$match": {"user_id": user["_id"], "date": {"$gte": start, "$lt": end}}},
        {"$group": {
            "_id": None,
            "total_spend": {"$sum": "$amount"},
            "count": {"$sum": 1},
            "categories": {"$push": "$category"},
            "amounts": {"$push": "$amount"},
            "confidences": {"$push": "$confidence"}
        }}
    ]
    
    result = await db.transactions.aggregate(pipeline).to_list(length=1)
    
    # Safe defaults if no data exists
    if not result or result[0]["count"] == 0:
        print("No transactions found for this month, returning safe defaults")
        return DashboardSummary(
            month=month,
            total_spend=0.0,
            top_category=None,
            top_category_spend=0.0,
            avg_confidence=None,
        )
    
    data = result[0]
    total_spend = float(data["total_spend"])
    
    print(f"Found {data['count']} transactions, total spend: {total_spend}")

    # Calculate top category from the aggregated data
    category_counts = {}
    for i, cat in enumerate(data["categories"]):
        if cat:
            category_counts[cat] = category_counts.get(cat, 0) + data["amounts"][i]
    
    top_category = None
    top_category_spend = 0.0
    if category_counts:
        top_category = max(category_counts, key=category_counts.get)
        top_category_spend = category_counts[top_category]
    
    # Calculate average confidence (filter out None values)
    valid_confidences = [c for c in data["confidences"] if c is not None]
    avg_confidence = sum(valid_confidences) / len(valid_confidences) if valid_confidences else None
    
    print(f"Top category: {top_category} ({top_category_spend})")
    print(f"Average confidence: {avg_confidence}")
    print(f"Category breakdown: {category_counts}")

    return DashboardSummary(
        month=month,
        total_spend=total_spend,
        top_category=top_category,
        top_category_spend=top_category_spend,
        avg_confidence=avg_confidence,
    )


@router.get("/trend", response_model=list[TrendPoint])
async def trend(user=Depends(get_current_user), db=Depends(get_db)):
    pipeline = [
        {"$match": {"user_id": user["_id"]}},
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m", "date": "$date"}},
                "total": {"$sum": "$amount"},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    out = []
    async for row in db.transactions.aggregate(pipeline):
        out.append(TrendPoint(month=row["_id"], total_spend=float(row.get("total") or 0.0)))
    return out


@router.get("/anomalies", response_model=list[AnomalyPoint])
async def anomalies(month: str, user=Depends(get_current_user), db=Depends(get_db)):
    if len(month) != 7 or month[4] != "-":
        raise HTTPException(status_code=400, detail="Month must be YYYY-MM")

    start = datetime.fromisoformat(month + "-01")
    if month[5:7] == "12":
        end = datetime.fromisoformat(str(int(month[:4]) + 1) + "-01-01")
    else:
        end = datetime.fromisoformat(month[:5] + f"{int(month[5:7]) + 1:02d}" + "-01")

    cursor = db.transactions.find({"user_id": user["_id"], "date": {"$gte": start, "$lt": end}})
    items = []
    async for doc in cursor:
        items.append(doc)

    if len(items) < 5:
        return []

    amounts = [float(d.get("amount") or 0.0) for d in items]
    mean = sum(amounts) / len(amounts)
    var = sum((x - mean) ** 2 for x in amounts) / len(amounts)
    std = var ** 0.5 if var > 0 else 1.0

    out = []
    for d in items:
        amt = float(d.get("amount") or 0.0)
        z = (amt - mean) / std
        if z >= 2.5:
            out.append(
                AnomalyPoint(
                    date=d.get("date").isoformat(),
                    amount=amt,
                    description=d.get("description") or "",
                    zscore=float(z),
                )
            )

    out.sort(key=lambda x: x.zscore, reverse=True)
    return out
