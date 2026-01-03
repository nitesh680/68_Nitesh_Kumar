import csv
import io
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response, StreamingResponse

from app.core.deps import get_current_user
from app.db.mongo import get_db

router = APIRouter()


@router.get("/transactions.csv")
async def export_transactions_csv(month: str | None = None, user=Depends(get_current_user), db=Depends(get_db)):
    query: dict = {"user_id": user["_id"]}

    if month:
        if len(month) != 7 or month[4] != "-":
            raise HTTPException(status_code=400, detail="Month must be YYYY-MM")
        start = datetime.fromisoformat(month + "-01")
        if month[5:7] == "12":
            end = datetime.fromisoformat(str(int(month[:4]) + 1) + "-01-01")
        else:
            end = datetime.fromisoformat(month[:5] + f"{int(month[5:7]) + 1:02d}" + "-01")
        query["date"] = {"$gte": start, "$lt": end}

    cursor = db.transactions.find(query).sort("date", -1)

    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["date", "amount", "description", "category", "confidence", "source", "explanation"])

    async for doc in cursor:
        writer.writerow(
            [
                doc.get("date").isoformat() if doc.get("date") else "",
                float(doc.get("amount") or 0.0),
                doc.get("description") or "",
                doc.get("category") or "",
                doc.get("confidence") if doc.get("confidence") is not None else "",
                doc.get("source") or "",
                doc.get("explanation") or "",
            ]
        )

    csv_bytes = buf.getvalue().encode("utf-8")
    filename = f"transactions{('-' + month) if month else ''}.csv"

    return Response(
        content=csv_bytes,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/transactions.pdf")
async def export_transactions_pdf(month: str | None = None, user=Depends(get_current_user), db=Depends(get_db)):
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except Exception as e:
        raise HTTPException(status_code=500, detail="reportlab not installed") from e

    query: dict = {"user_id": user["_id"]}

    if month:
        if len(month) != 7 or month[4] != "-":
            raise HTTPException(status_code=400, detail="Month must be YYYY-MM")
        start = datetime.fromisoformat(month + "-01")
        if month[5:7] == "12":
            end = datetime.fromisoformat(str(int(month[:4]) + 1) + "-01-01")
        else:
            end = datetime.fromisoformat(month[:5] + f"{int(month[5:7]) + 1:02d}" + "-01")
        query["date"] = {"$gte": start, "$lt": end}

    cursor = db.transactions.find(query).sort("date", -1).limit(200)

    pdf_buf = io.BytesIO()
    c = canvas.Canvas(pdf_buf, pagesize=letter)
    width, height = letter

    title = f"Transactions{(' - ' + month) if month else ''}"
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, height - 40, title)

    y = height - 70
    c.setFont("Helvetica", 9)

    header = "DATE | AMOUNT | CATEGORY | DESCRIPTION"
    c.drawString(40, y, header)
    y -= 14

    async for doc in cursor:
        if y < 60:
            c.showPage()
            y = height - 50
            c.setFont("Helvetica", 9)

        date_str = doc.get("date").strftime("%Y-%m-%d") if doc.get("date") else ""
        amt = float(doc.get("amount") or 0.0)
        cat = (doc.get("category") or "")[:20]
        desc = (doc.get("description") or "")[:60]
        line = f"{date_str} | {amt:.2f} | {cat} | {desc}"
        c.drawString(40, y, line)
        y -= 12

    c.save()
    pdf_buf.seek(0)

    filename = f"transactions{('-' + month) if month else ''}.pdf"
    return StreamingResponse(
        pdf_buf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
