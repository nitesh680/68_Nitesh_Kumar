# Personal Expense Categorization Assistant

A full-stack application to upload transactions, automatically categorize them (Rules → ML → Gemini), and view dashboards, analytics, and AI-powered financial insights.

## Tech Stack

- **Backend**: FastAPI + MongoDB (Motor)
- **Frontend**: React (Vite) + TailwindCSS + React Query
- **ML**: TF-IDF + Logistic Regression (optional; artifacts saved locally)
- **LLM / AI**: Gemini (optional)

## Key Features

- **Authentication**: Signup/Login with JWT
- **Transactions**: Create and CSV upload
- **Auto categorization**: Rules → ML model (joblib) → Gemini fallback
- **Analytics**: Dashboard KPIs, trend, anomalies
- **AI Insights**:
  - Monthly + yearly summaries
  - Income vs expenses (income rows supported)
  - Wasteful spending signals
  - Budget alerts (uses Settings monthly budget)
  - Health score + next-month prediction
- **Profile**:
  - Edit profile fields
  - Avatar upload served via `/uploads/...`
- **Export**: CSV and PDF exports

---

# Quick Start

## Requirements

- **Python** 3.10+
- **Node.js** 18+ (Node 20 recommended)
- **MongoDB** running locally or accessible via URI

## Backend Setup (FastAPI)

1) Create `backend/.env` (required)

Example:

```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=expense_ai
JWT_SECRET=change_me
JWT_ALGORITHM=HS256
CORS_ORIGINS=http://localhost:5173
GEMINI_API_KEY=
MODEL_DIR=./artifacts
CONFIDENCE_THRESHOLD=0.65
```

2) Install dependencies

```bash
pip install -r backend/requirements.txt
```

3) Run the API

From the `backend/` folder:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005 --reload
```

Health check:

```text
GET http://localhost:8005/api/health
```

API docs:

```text
http://localhost:8005/docs
```

## Frontend Setup (React/Vite)

1) Install dependencies

```bash
cd frontend
npm install
```

2) Configure API base URL

`frontend/src/lib/api.ts` reads:

- `VITE_API_BASE_URL` (recommended)
- fallback: `http://localhost:8000`

Create or edit `frontend/.env`:

```env
VITE_API_BASE_URL=http://localhost:8005
```

3) Run the frontend

```bash
npm run dev
```

Open:

- `http://localhost:5173` (or the next available port if 5173 is busy)

---

# CSV Upload Format

CSV must include columns:

- `date` (YYYY-MM-DD)
- `amount` (number)
- `description` (string)

Income rows are supported when the category/description indicates **Income/Salary**.

---

# API Overview (Main Routes)

All routes are prefixed with `/api`.

## Auth

- `POST /api/auth/signup`
- `POST /api/auth/login`
- `GET /api/auth/me`

## Transactions

- `POST /api/transactions` (create one)
- `POST /api/transactions/upload` (CSV upload)
- `GET /api/transactions/recent`

## Analytics

- `GET /api/analytics/dashboard?month=YYYY-MM`
- `GET /api/analytics/trend`
- `GET /api/analytics/anomalies?month=YYYY-MM`

## Insights

- `GET /api/insights/summary?month=YYYY-MM` (classic summary)
- `GET /api/insights/advanced?month=YYYY-MM&year=YYYY&budget_inr=12345` (advanced insights)

## Export

- `GET /api/export/transactions.csv?month=YYYY-MM`
- `GET /api/export/transactions.pdf?month=YYYY-MM`

## Users / Profile

- `GET /api/users/profile`
- `PATCH /api/users/profile`
- `POST /api/users/profile/avatar`

---

# File Structure & Responsibilities (File-by-File)

Below is a detailed description of the purpose of each important file in this repository.

> Notes
>
>- `node_modules/`, `dist/`, `__pycache__/` are build artifacts and not documented in detail.
>- Paths below are relative to the repository root.

---

## Root

- **`.gitignore`**
  Controls which files are excluded from Git (build outputs, caches, secrets).
- **`README.md`**
  You are reading it: project overview, setup, and file responsibilities.
- **`GUIDELINES.md`**
  Hackathon/event guidelines and submission requirements.
- **`IMPLEMENTATION_SUMMARY.md`**
  A high-level summary of completed features and testing notes.
- **`package.json`**
  Root-level dev dependencies (currently includes React Query for workspace tooling).
- **`package-lock.json`**
  Root lockfile (may exist due to workspace tooling).
- **`sample_transactions.csv`**
  Example CSV to test uploads.
- **`fix_dates.py`**
  Utility script to call a backend endpoint to normalize/adjust transaction dates and then test Insights.
- **`test_api.py`**
  Simple smoke test for backend endpoints.
- **`test_complete_system.py`**
  End-to-end test script: health, upload, analytics, insights, trend, recent transactions.
- **`test_dashboard_fix.py`**
  Performance-oriented test script for dashboard/insights/trend endpoints.
- **`test_dashboard.html`**
  Small standalone HTML page to test dashboard endpoints manually.
- **`archive (2)/...`**
  Archived/raw datasets (original CSVs); these may not match the app’s required CSV format.

---

## Backend (`backend/`)

- **`backend/requirements.txt`**
  Python dependency pins for FastAPI, MongoDB drivers, ML, exports (reportlab), and Gemini integration.
- **`backend/.env`**
  Local environment variables (not committed). Defines MongoDB URI, JWT secret, Gemini key, etc.
- **`backend/artifacts/`**
  ML model artifacts (joblib).
  - `expense_model.joblib` preferred custom model
  - `model.joblib` fallback default model
- **`backend/uploads/`**
  Uploaded static assets (currently used for profile avatars).
- **`backend/train.csv`, `backend/train_real.csv`, `backend/train_real_balanced.csv`**
  Training datasets used by the ML training pipeline.

### Backend Application Package: `backend/app/`

- **`backend/app/__init__.py`**
  Marks `app` as a Python package.
- **`backend/app/main.py`**
  FastAPI application entry point:
  - configures CORS
  - includes routers under `/api/...`
  - mounts `/uploads` static directory
  - exposes `/api/health`

#### `backend/app/core/`

- **`backend/app/core/config.py`**
  Central settings via `pydantic-settings`:
  - MongoDB connection
  - JWT configuration
  - Gemini API key
  - CORS origins
  - ML artifacts folder
- **`backend/app/core/deps.py`**
  Dependency injection helpers:
  - `get_current_user()` reads JWT from `Authorization: Bearer ...` and loads the user from MongoDB.
- **`backend/app/core/security.py`**
  Security utilities:
  - password hashing/verification
  - JWT token creation
- **`backend/app/core/__init__.py`**
  Package marker.

#### `backend/app/db/`

- **`backend/app/db/mongo.py`**
  MongoDB client and database getter using Motor (`AsyncIOMotorClient`).
- **`backend/app/db/__init__.py`**
  Package marker.

#### `backend/app/schemas/` (Pydantic models)

- **`backend/app/schemas/auth.py`**
  Request/response schemas for signup/login and `UserPublic`.
- **`backend/app/schemas/transactions.py`**
  Transaction request/response schemas, upload response schema, and month summary schema.
- **`backend/app/schemas/analytics.py`**
  Analytics response schemas: dashboard summary, trend points, anomalies.
- **`backend/app/schemas/model.py`**
  ML training and prediction request/response schemas.
- **`backend/app/schemas/users.py`**
  Profile schemas for viewing/updating user profile and avatar upload response.
- **`backend/app/schemas/__init__.py`**
  Package marker.

#### `backend/app/routers/` (HTTP API routes)

- **`backend/app/routers/__init__.py`**
  Imports router modules for convenience.
- **`backend/app/routers/auth.py`**
  Auth endpoints:
  - signup/login
  - `/me` user info
- **`backend/app/routers/transactions.py`**
  Transaction endpoints:
  - create single transaction
  - upload CSV (pandas parsing)
  - recent transactions
  - categorization-only endpoint
- **`backend/app/routers/analytics.py`**
  Dashboard analytics endpoints:
  - monthly dashboard summary
  - trend
  - anomaly detection
- **`backend/app/routers/insights.py`**
  AI Insights endpoints:
  - `/summary` data-driven summary with optional Gemini enhancement
  - `/advanced` income-aware monthly+yearly insights, budget alerts, health score, waste signals, prediction, chart data
- **`backend/app/routers/export.py`**
  Export endpoints:
  - CSV export
  - PDF export (ReportLab)
- **`backend/app/routers/model.py`**
  ML endpoints:
  - train from CSV path
  - train via upload
  - predict category for a description
- **`backend/app/routers/users.py`**
  Profile endpoints:
  - get/update profile
  - upload avatar image (stored under `backend/uploads/avatars/`)

#### `backend/app/services/` (business logic)

- **`backend/app/services/categorizer.py`**
  Categorization orchestration:
  - rules first
  - then ML model if available
  - then Gemini fallback
- **`backend/app/services/gemini.py`**
  Gemini categorization client (LangChain Google GenAI) with JSON parsing + safe fallback.
- **`backend/app/services/__init__.py`**
  Package marker.

#### `backend/app/ml/` (ML utilities)

- **`backend/app/ml/model_store.py`**
  Load/save ML artifacts (`expense_model.joblib` preferred, `model.joblib` fallback).
- **`backend/app/ml/trainer.py`**
  Training pipeline:
  - TF-IDF vectorizer + Logistic Regression
  - saves model artifacts
- **`backend/app/ml/rules.py`**
  Simple regex-based categorization rules.
- **`backend/app/ml/__init__.py`**
  Package marker.

---

## Frontend (`frontend/`)

- **`frontend/package.json`**
  Frontend dependencies and scripts (`npm run dev`, `npm run build`).
- **`frontend/package-lock.json`**
  Lockfile for exact dependency versions.
- **`frontend/vite.config.ts`**
  Vite configuration (React plugin).
- **`frontend/tailwind.config.js`**
  Tailwind configuration (file scanning paths).
- **`frontend/postcss.config.js`**
  PostCSS setup (Tailwind + autoprefixer).
- **`frontend/index.html`**
  Single-page app HTML shell for Vite.
- **`frontend/.env`**
  Local frontend environment variables (e.g. `VITE_API_BASE_URL`).

### Frontend Source: `frontend/src/`

- **`frontend/src/main.tsx`**
  React entry point:
  - mounts the app
  - sets up React Query + Router
- **`frontend/src/App.tsx`**
  Top-level routes and ProtectedRoute wiring.
- **`frontend/src/index.css`**
  Tailwind base + global styling.
- **`frontend/src/App.css`**
  Minimal CSS placeholder.
- **`frontend/src/types.ts`**
  Shared TypeScript types for API responses.

#### `frontend/src/lib/`

- **`frontend/src/lib/api.ts`**
  Axios client + `setAuthToken()`.
  Uses `VITE_API_BASE_URL` to set the backend base URL.
- **`frontend/src/lib/storage.ts`**
  Token storage helpers: `getToken`, `setToken`, `clearToken`.
- **`frontend/src/lib/format.ts`**
  Formatting helpers:
  - INR currency formatting
  - `ymNow()` (current YYYY-MM)

#### `frontend/src/hooks/`

- **`frontend/src/hooks/useProfile.ts`**
  React Query hooks for profile:
  - fetch profile
  - update profile
  - upload avatar

#### `frontend/src/components/`

- **`frontend/src/components/Layout.tsx`**
  Global layout wrapper with background effects and page container.
- **`frontend/src/components/Header.tsx`**
  Top navigation bar, routes, login/logout logic.
- **`frontend/src/components/Footer.tsx`**
  Responsive footer with navigation links.
- **`frontend/src/components/UserProfileAvatar.tsx`**
  Clickable profile avatar in navbar with dropdown (Profile/Settings/Logout).
- **`frontend/src/components/ProtectedRoute.tsx`**
  Redirects to `/login` when no token exists.
- **`frontend/src/components/Navbar.tsx`**
  Additional navigation component (if used by specific pages).
- **`frontend/src/components/Card.tsx`**
  Reusable Card UI component; exports both named and default to avoid import mismatches.
- **`frontend/src/components/Button.tsx`**
  Reusable button component with variants.
- **`frontend/src/components/Input.tsx`**
  Reusable input component; supports optional `error` display.

#### `frontend/src/pages/`

- **`frontend/src/pages/Login.tsx`**
  Login form and token storage.
- **`frontend/src/pages/Signup.tsx`**
  Signup form and token storage.
- **`frontend/src/pages/Dashboard.tsx`**
  Main dashboard view:
  - month selection
  - dashboard KPIs
  - trend and recent transactions
- **`frontend/src/pages/Upload.tsx`**
  CSV upload UI; invalidates queries after upload.
- **`frontend/src/pages/History.tsx`**
  Recent transaction list and filters.
- **`frontend/src/pages/Export.tsx`**
  Export transactions to CSV/PDF.
- **`frontend/src/pages/Insights.tsx`**
  Advanced AI Insights dashboard:
  - KPIs (income/expenses/savings/health)
  - alerts, waste signals, prediction
  - responsive bar/pie charts
- **`frontend/src/pages/Profile.tsx`**
  Profile page:
  - edit name/mobile/DOB
  - upload avatar
- **`frontend/src/pages/Settings.tsx`**
  User preferences (currently monthly budget stored in localStorage).

---

# Status

- **README file documentation**: complete and kept in sync with current code.

