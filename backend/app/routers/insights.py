from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.deps import get_current_user
from app.db.mongo import get_db
from langchain_google_genai import ChatGoogleGenerativeAI

router = APIRouter()


@router.get("/summary")
async def monthly_ai_summary(month: str, user=Depends(get_current_user), db=Depends(get_db)):
    if not settings.GEMINI_API_KEY:
        raise HTTPException(status_code=400, detail="GEMINI_API_KEY not configured")

    if len(month) != 7 or month[4] != "-":
        raise HTTPException(status_code=400, detail="Month must be YYYY-MM")

    start = datetime.fromisoformat(month + "-01")
    if month[5:7] == "12":
        end = datetime.fromisoformat(str(int(month[:4]) + 1) + "-01-01")
    else:
        end = datetime.fromisoformat(month[:5] + f"{int(month[5:7]) + 1:02d}" + "-01")

    pipeline = [
        {"$match": {"user_id": user["_id"], "date": {"$gte": start, "$lt": end}}},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
        {"$sort": {"total": -1}},
    ]

    rows = []
    async for row in db.transactions.aggregate(pipeline):
        rows.append({"category": row.get("_id") or "Other", "total": float(row.get("total") or 0.0)})

    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GEMINI_API_KEY)
    prompt = (
        "You are a personal finance assistant. Summarize the user's spending for the month. "
        "Provide: 1) short summary 2) top categories 3) one actionable suggestion. "
        "Keep it under 120 words.\n\n"
        f"Month: {month}\nCategory totals (descending): {rows}"
    )
    resp = llm.invoke(prompt)
    return {"month": month, "summary": (resp.content or "").strip(), "breakdown": rows}
