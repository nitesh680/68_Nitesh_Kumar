# Personal Expense Categorization Assistant

A full-stack app that helps you upload or add transactions, automatically categorize them (rules → ML → Gemini), and view dashboards/analytics.

## Tech Stack

- Backend: FastAPI + MongoDB (Motor)
- Frontend: React (Vite) + TailwindCSS
- ML: TF-IDF + Logistic Regression (optional; artifacts saved locally)
- LLM: Gemini (optional)

## Project Structure

- `backend/` FastAPI app
- `frontend/` React app
- `archive (2)/` sample CSVs (your original dataset; no `description` column)

## Requirements

- Python 3.10+
- Node.js 20.x (works with Vite 5 in this repo)
- MongoDB running locally

## Backend Setup

### 1) Create `backend/.env`

Copy `backend/.env.example` → `backend/.env` and set values:


### 2) Install deps

```bash
pip install -r requirements.txt
```

### 3) Run API

```bash
uvicorn app.main:app --reload --port 8000
```

Health check:
- `GET http://localhost:8000/api/health`

## Frontend Setup

```bash
npm install
npm run dev
```

Open:
- `http://localhost:5173`

## CSV Upload Format (Option B)

Your current dataset does not contain descriptions, so uploads require `description`.

CSV must include columns:
- `date`
- `amount`
- `description`

