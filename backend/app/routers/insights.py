from datetime import datetime
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException

from app.core.config import settings
from app.core.deps import get_current_user
from app.db.mongo import get_db
from langchain_google_genai import ChatGoogleGenerativeAI

router = APIRouter()


def _parse_month(month: str) -> tuple[datetime, datetime]:
    if len(month) != 7 or month[4] != "-":
        raise HTTPException(status_code=400, detail="Month must be YYYY-MM")

    start = datetime.fromisoformat(month + "-01")
    if month[5:7] == "12":
        end = datetime.fromisoformat(str(int(month[:4]) + 1) + "-01-01")
    else:
        end = datetime.fromisoformat(month[:5] + f"{int(month[5:7]) + 1:02d}" + "-01")
    return start, end


def _is_income_category(cat: str | None) -> bool:
    c = (cat or "").strip().lower()
    return c in {"income", "salary", "payroll", "salary credit", "salary credited"} or "salary" in c or "income" in c


@router.get("/summary")
async def monthly_ai_summary(month: str, user=Depends(get_current_user), db=Depends(get_db)):
    start, end = _parse_month(month)

    print(f"Insights request for user: {user['_id']}, month: {month}")
    print(f"Date range: {start} to {end}")

    # Debug: Check what transactions exist for this user
    debug_pipeline = [
        {"$match": {"user_id": user["_id"]}},
        {"$sort": {"date": -1}},
        {"$limit": 10},
        {"$project": {"date": 1, "amount": 1, "category": 1, "description": 1}}
    ]
    
    debug_transactions = []
    async for doc in db.transactions.aggregate(debug_pipeline):
        debug_transactions.append({
            "date": str(doc.get("date")),
            "amount": doc.get("amount"),
            "category": doc.get("category"),
            "description": doc.get("description", "")[:30]
        })
    
    print(f"Sample transactions for user: {debug_transactions}")
    
    # Check what months actually have data
    months_pipeline = [
        {"$match": {"user_id": user["_id"]}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$date"}}, "count": {"$sum": 1}}},
        {"$sort": {"_id": -1}}
    ]
    
    available_months = []
    async for row in db.transactions.aggregate(months_pipeline):
        available_months.append({"month": row["_id"], "count": row["count"]})
    
    print(f"Available months with data: {available_months}")

    # Get category breakdown for the month
    pipeline = [
        {"$match": {"user_id": user["_id"], "date": {"$gte": start, "$lt": end}}},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}},
        {"$sort": {"total": -1}},
    ]

    rows = []
    async for row in db.transactions.aggregate(pipeline):
        rows.append({
            "category": row.get("_id") or "Other", 
            "total": float(row.get("total") or 0.0),
            "count": row.get("count", 0)
        })

    print(f"Found {len(rows)} categories for insights in {month}: {rows}")

    # If no data found for the specific month, show proper message with available months
    if len(rows) == 0:
        print("No data found for specific month")
        
        # Create message with available months
        if available_months:
            months_list = ", ".join([f"{m['month']} ({m['count']} transactions)" for m in available_months[:5]])
            message = f"No spending data found for {datetime.strptime(month, '%Y-%m').strftime('%B %Y')}. Available months: {months_list}."
        else:
            message = f"No spending data found for {datetime.strptime(month, '%Y-%m').strftime('%B %Y')}. Upload transactions to see insights."
        
        return {
            "month": month,
            "summary": message,
            "breakdown": [],
            "ai_enabled": False,
            "total_spending": 0.0,
            "transaction_count": 0,
            "avg_confidence": None,
            "available_months": available_months
        }
    else:
        month_name = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
    
    # Calculate metrics
    total_spending = sum(row["total"] for row in rows)
    top_category = rows[0]["category"] if rows else "Other"
    top_category_spend = float(rows[0]["total"]) if rows else 0.0
    transaction_count = sum(row["count"] for row in rows)
    
    # Calculate average confidence (month-scoped)
    confidence_pipeline = [
        {
            "$match": {
                "user_id": user["_id"],
                "date": {"$gte": start, "$lt": end},
                "confidence": {"$ne": None},
            }
        },
        {"$group": {"_id": None, "avg_confidence": {"$avg": "$confidence"}}},
    ]
    
    confidence_result = await db.transactions.aggregate(confidence_pipeline).to_list(length=1)
    avg_confidence = float(confidence_result[0]["avg_confidence"]) if confidence_result else None

    # Previous month comparison (same user)
    prev_total_spending = None
    try:
        y = int(month[:4])
        m = int(month[5:7])
        if m == 1:
            prev_y, prev_m = y - 1, 12
        else:
            prev_y, prev_m = y, m - 1

        prev_start = datetime(prev_y, prev_m, 1)
        prev_end = datetime(y, m, 1)

        prev_total_pipeline = [
            {"$match": {"user_id": user["_id"], "date": {"$gte": prev_start, "$lt": prev_end}}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}},
        ]
        prev_total_res = await db.transactions.aggregate(prev_total_pipeline).to_list(length=1)
        if prev_total_res:
            prev_total_spending = float(prev_total_res[0].get("total") or 0.0)
    except Exception as e:
        print(f"Prev-month calc failed: {e}")
        prev_total_spending = None

    spend_change = None
    spend_change_pct = None
    if prev_total_spending is not None:
        spend_change = total_spending - prev_total_spending
        if prev_total_spending > 0:
            spend_change_pct = spend_change / prev_total_spending

    # Data-driven 'why' signals from descriptions (top keywords + recurring descriptions)
    keywords: list[str] = []
    recurring: list[dict] = []
    try:
        desc_cursor = db.transactions.find(
            {"user_id": user["_id"], "date": {"$gte": start, "$lt": end}},
            {"description": 1, "category": 1, "amount": 1},
        ).limit(300)

        descriptions: list[str] = []
        top_cat_descriptions: list[str] = []
        async for d in desc_cursor:
            desc = str(d.get("description") or "").strip()
            if not desc:
                continue
            descriptions.append(desc)
            if (d.get("category") or "Other") == top_category:
                top_cat_descriptions.append(desc)

        import re

        stop = {
            "the",
            "and",
            "to",
            "of",
            "in",
            "for",
            "on",
            "at",
            "with",
            "a",
            "an",
            "from",
            "payment",
            "upi",
            "card",
            "debit",
            "credit",
            "txn",
            "transaction",
        }

        def tokens(text: str) -> list[str]:
            raw = re.findall(r"[A-Za-z0-9]{3,}", text.lower())
            return [t for t in raw if t not in stop]

        from collections import Counter

        kw_counter = Counter()
        for desc in top_cat_descriptions[:200]:
            kw_counter.update(tokens(desc))
        keywords = [k for k, _ in kw_counter.most_common(5)]

        rec_counter = Counter([d.lower()[:60] for d in descriptions])
        recurring = [
            {"description": k, "count": int(v)}
            for k, v in rec_counter.most_common(5)
            if v >= 2
        ]
    except Exception as e:
        print(f"Description analysis failed: {e}")
    
    if total_spending > 0:
        # Get second top category if available
        second_category = rows[1]["category"] if len(rows) > 1 else None

        summary = f"In {month_name}, you spent ₹{total_spending:.2f}. {top_category} was the top category at ₹{top_category_spend:.2f}"
        if second_category:
            summary += f", followed by {second_category}"
        summary += "."
        
        if avg_confidence:
            summary += f" Average prediction confidence was {avg_confidence:.2f}."
        else:
            summary += " Prediction confidence data not available."
    else:
        summary = f"No spending data found for {month_name}. Upload transactions to see insights here."

    # Prepare confidence string safely
    confidence_str = f"{avg_confidence:.2f}" if avg_confidence is not None else "N/A"
    
    # Try Gemini if API key is available, otherwise use data-based summary
    ai_summary = summary
    ai_enabled = False
    
    if settings.GEMINI_API_KEY:
        try:
            # Use supported model
            import asyncio

            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.2,
            )

            why_bits = []
            if keywords:
                why_bits.append(f"Top keywords in {top_category}: {', '.join(keywords)}")
            if recurring:
                why_bits.append(
                    "Recurring descriptions: "
                    + "; ".join([f"{r['description']} (x{r['count']})" for r in recurring[:3]])
                )
            why_text = " | ".join(why_bits) if why_bits else "No strong description patterns found."

            prev_text = "N/A"
            if prev_total_spending is not None:
                prev_text = f"₹{prev_total_spending:.2f}"

            change_text = "N/A"
            if spend_change is not None:
                if spend_change_pct is not None:
                    change_text = f"₹{spend_change:.2f} ({spend_change_pct*100:.1f}%)"
                else:
                    change_text = f"₹{spend_change:.2f}"

            prompt = (
                f"You are a personal finance coach. Create a FAST summary for {month_name} using ONLY the user's data. "
                f"Output 5-7 short bullet points max.\n"
                f"Data: total=₹{total_spending:.2f}, top_category={top_category}, top_category_spend=₹{top_category_spend:.2f}, "
                f"second_category={rows[1]['category'] if len(rows) > 1 else 'N/A'}, tx_count={transaction_count}, avg_confidence={confidence_str}.\n"
                f"Previous month total={prev_text}, change_vs_prev={change_text}.\n"
                f"Why signals: {why_text}.\n"
                f"Requirements:\n"
                f"- Mention top category and spend amount.\n"
                f"- Give 1-2 likely reasons based on the WHY signals (do not invent merchants).\n"
                f"- Compare previous vs current month briefly.\n"
                f"- Give 3 actionable tips to reduce future spending + a simple budget suggestion for next month."
            )
            
            # Keep insights fast and never hang the UI
            resp = await asyncio.wait_for(llm.ainvoke(prompt), timeout=6.0)
            ai_summary = resp.content.strip() if resp.content else summary
            ai_enabled = True
            print("Gemini AI summary generated successfully")
            
        except Exception as e:
            print(f"Gemini AI failed: {e}, using data-based summary")
            ai_summary = summary
    else:
        print("No Gemini API key, using data-based summary")

    return {
        "month": month,
        "summary": ai_summary,
        "breakdown": rows,
        "ai_enabled": ai_enabled,
        "total_spending": total_spending,
        "transaction_count": transaction_count,
        "avg_confidence": avg_confidence,
        "top_category": top_category,
        "top_category_spend": top_category_spend,
        "prev_total_spending": prev_total_spending,
        "spend_change": spend_change,
        "spend_change_pct": spend_change_pct,
    }


@router.get("/advanced")
async def advanced_ai_insights(
    month: str,
    year: str | None = None,
    budget_inr: float | None = None,
    user=Depends(get_current_user),
    db=Depends(get_db),
):
    start, end = _parse_month(month)
    y = int(month[:4])
    year_val = int(year) if year else y

    year_start = datetime(year_val, 1, 1)
    year_end = datetime(year_val + 1, 1, 1)

    match_month = {"user_id": user["_id"], "date": {"$gte": start, "$lt": end}}
    match_year = {"user_id": user["_id"], "date": {"$gte": year_start, "$lt": year_end}}

    tx_cursor = db.transactions.find(match_month, {"amount": 1, "category": 1, "description": 1, "date": 1}).limit(5000)
    month_txs: list[dict] = []
    async for t in tx_cursor:
        month_txs.append(t)

    if not month_txs:
        return {
            "month": month,
            "year": str(year_val),
            "ai_enabled": False,
            "summary": f"No data found for {month}. Upload transactions to see insights.",
            "kpis": {
                "income": 0.0,
                "expenses": 0.0,
                "savings": 0.0,
                "health_score": 0,
                "budget": budget_inr,
                "budget_status": "no_data",
            },
            "charts": {"bar_by_category": [], "pie_distribution": []},
            "wasteful": [],
            "alerts": [],
            "prediction": {"next_month_expense": 0.0, "basis": "no_data"},
            "yearly": {"income": 0.0, "expenses": 0.0, "savings": 0.0, "top_categories": []},
        }

    income_total = 0.0
    expense_total = 0.0
    cat_exp: dict[str, float] = {}
    cat_income: dict[str, float] = {}
    descs: list[str] = []

    for t in month_txs:
        amt = float(t.get("amount") or 0.0)
        cat = (t.get("category") or "Other")
        desc = str(t.get("description") or "").strip()
        if desc:
            descs.append(desc)
        if _is_income_category(cat):
            income_total += amt
            cat_income[cat] = cat_income.get(cat, 0.0) + amt
        else:
            expense_total += amt
            cat_exp[cat] = cat_exp.get(cat, 0.0) + amt

    savings = income_total - expense_total
    saving_rate = (savings / income_total) if income_total > 0 else None

    # Budget status
    budget_status = "no_budget"
    if budget_inr is not None:
        if expense_total <= budget_inr:
            budget_status = "within_budget"
        elif expense_total <= budget_inr * 1.1:
            budget_status = "near_limit"
        else:
            budget_status = "over_budget"

    # Wasteful spending: compare category spends vs previous month + recurring descriptions
    prev_total_expenses = None
    prev_cat_exp: dict[str, float] = {}
    try:
        m = int(month[5:7])
        if m == 1:
            prev_month = f"{y-1}-12"
        else:
            prev_month = f"{y}-{m-1:02d}"
        prev_start, prev_end = _parse_month(prev_month)
        prev_cursor = db.transactions.find(
            {"user_id": user["_id"], "date": {"$gte": prev_start, "$lt": prev_end}},
            {"amount": 1, "category": 1, "description": 1},
        ).limit(5000)
        prev_exp_total = 0.0
        async for t in prev_cursor:
            cat = (t.get("category") or "Other")
            if _is_income_category(cat):
                continue
            amt = float(t.get("amount") or 0.0)
            prev_exp_total += amt
            prev_cat_exp[cat] = prev_cat_exp.get(cat, 0.0) + amt
        prev_total_expenses = prev_exp_total
    except Exception as e:
        print(f"Prev-month advanced calc failed: {e}")

    wasteful: list[dict] = []
    if prev_total_expenses is not None and prev_total_expenses > 0:
        for cat, total in sorted(cat_exp.items(), key=lambda x: x[1], reverse=True)[:8]:
            prev = float(prev_cat_exp.get(cat, 0.0))
            if prev <= 0:
                continue
            delta = total - prev
            pct = delta / prev
            if pct >= 0.25 and delta >= max(500.0, prev * 0.1):
                wasteful.append(
                    {
                        "type": "category_spike",
                        "category": cat,
                        "message": f"You spent more on {cat} than last month (₹{prev:.0f} → ₹{total:.0f}).",
                        "change_pct": pct,
                    }
                )

    rec_counter = Counter([d.lower()[:60] for d in descs])
    for d, c in rec_counter.most_common(5):
        if c >= 3:
            wasteful.append(
                {
                    "type": "repeat_merchant",
                    "message": f"Recurring spend pattern: '{d}' appeared {int(c)} times.",
                    "count": int(c),
                }
            )

    # Health score (0-100)
    score = 100
    if income_total > 0:
        if saving_rate is not None:
            if saving_rate < 0:
                score -= 50
            elif saving_rate < 0.05:
                score -= 25
            elif saving_rate < 0.15:
                score -= 10
        if budget_inr is not None and expense_total > budget_inr:
            over = (expense_total - budget_inr) / max(1.0, budget_inr)
            score -= int(min(25, over * 50))
    else:
        # If income not present, base score on stability
        score -= 15

    if len(wasteful) >= 3:
        score -= 10
    score = max(0, min(100, score))

    # Next-month prediction: moving average of last 3 months expenses
    next_pred = 0.0
    basis = "insufficient_history"
    try:
        history_pipeline = [
            {"$match": {"user_id": user["_id"], "date": {"$lt": end}}},
            {
                "$addFields": {
                    "is_income": {
                        "$regexMatch": {"input": {"$toLower": {"$ifNull": ["$category", ""]}}, "regex": "(income|salary)"}
                    }
                }
            },
            {"$match": {"is_income": False}},
            {"$group": {"_id": {"$dateToString": {"format": "%Y-%m", "date": "$date"}}, "total": {"$sum": "$amount"}}},
            {"$sort": {"_id": -1}},
            {"$limit": 4},
        ]
        hist = await db.transactions.aggregate(history_pipeline).to_list(length=10)
        totals = [float(h.get("total") or 0.0) for h in hist if h.get("_id")]
        if len(totals) >= 2:
            # ignore current month if included by pipeline ordering, take last 3 months including current
            last3 = totals[:3]
            next_pred = sum(last3) / len(last3)
            basis = f"avg_last_{len(last3)}_months"
    except Exception as e:
        print(f"Prediction calc failed: {e}")

    # Yearly summary
    year_pipeline = [
        {"$match": match_year},
        {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
        {"$sort": {"total": -1}},
    ]
    year_rows = await db.transactions.aggregate(year_pipeline).to_list(length=500)
    yearly_income = 0.0
    yearly_expenses = 0.0
    yearly_top: list[dict] = []
    for r in year_rows:
        cat = r.get("_id") or "Other"
        total = float(r.get("total") or 0.0)
        if _is_income_category(cat):
            yearly_income += total
        else:
            yearly_expenses += total
            yearly_top.append({"category": cat, "total": total})
    yearly_savings = yearly_income - yearly_expenses
    yearly_top = yearly_top[:8]

    # Charts payload
    bar_by_category = [
        {"category": k, "total": float(v)}
        for k, v in sorted(cat_exp.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    pie_distribution = []
    if expense_total > 0:
        for r in bar_by_category:
            pie_distribution.append(
                {
                    "category": r["category"],
                    "value": r["total"],
                    "pct": r["total"] / expense_total,
                }
            )

    alerts: list[dict] = []
    if budget_status == "near_limit":
        alerts.append({"type": "budget", "level": "warning", "message": "You are close to your monthly budget."})
    if budget_status == "over_budget":
        alerts.append({"type": "budget", "level": "danger", "message": "You have exceeded your monthly budget."})
    if income_total > 0 and savings < 0:
        alerts.append({"type": "savings", "level": "danger", "message": "Expenses are higher than income this month."})

    # Base data-driven summary
    month_name = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
    base_summary = (
        f"{month_name}: Income ₹{income_total:.0f}, Expenses ₹{expense_total:.0f}, Savings ₹{savings:.0f}. "
        f"Health score {score}/100."
    )

    ai_summary = base_summary
    ai_enabled = False
    if settings.GEMINI_API_KEY:
        try:
            import asyncio

            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.2,
            )

            budget_text = "N/A" if budget_inr is None else f"₹{budget_inr:.0f} ({budget_status})"
            top_cats_text = ", ".join([f"{x['category']} ₹{x['total']:.0f}" for x in bar_by_category[:5]]) or "N/A"
            waste_text = "; ".join([w.get("message", "") for w in wasteful[:4]]) or "No clear waste patterns."
            pred_text = f"₹{next_pred:.0f} ({basis})"
            yr_text = f"Income ₹{yearly_income:.0f}, Expenses ₹{yearly_expenses:.0f}, Savings ₹{yearly_savings:.0f}"

            prompt = (
                f"You are an expert financial analyst. Generate a concise but advanced insights report using ONLY the user's data.\n"
                f"Month={month_name}. KPIs: income=₹{income_total:.0f}, expenses=₹{expense_total:.0f}, savings=₹{savings:.0f}, health_score={score}/100, budget={budget_text}.\n"
                f"Top expense categories: {top_cats_text}.\n"
                f"Wasteful signals: {waste_text}.\n"
                f"Next-month expense prediction: {pred_text}.\n"
                f"Yearly summary for {year_val}: {yr_text}.\n"
                f"Output requirements (max 10 bullet points):\n"
                f"- Monthly summary and yearly context\n"
                f"- Identify wasteful spending clearly in simple language\n"
                f"- Suggest smart income utilization (savings, emergency fund, goal allocation)\n"
                f"- Provide 2-3 concrete actions for next month (include ₹ numbers when possible)\n"
                f"- Mention budget alert if relevant\n"
            )
            resp = await asyncio.wait_for(llm.ainvoke(prompt), timeout=7.0)
            if resp and resp.content:
                ai_summary = resp.content.strip()
                ai_enabled = True
        except Exception as e:
            print(f"Gemini advanced insights failed: {e}")

    return {
        "month": month,
        "year": str(year_val),
        "ai_enabled": ai_enabled,
        "summary": ai_summary,
        "kpis": {
            "income": income_total,
            "expenses": expense_total,
            "savings": savings,
            "health_score": score,
            "budget": budget_inr,
            "budget_status": budget_status,
        },
        "charts": {"bar_by_category": bar_by_category, "pie_distribution": pie_distribution},
        "wasteful": wasteful,
        "alerts": alerts,
        "prediction": {"next_month_expense": next_pred, "basis": basis},
        "yearly": {
            "income": yearly_income,
            "expenses": yearly_expenses,
            "savings": yearly_savings,
            "top_categories": yearly_top,
        },
    }
