from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.db.mongo import get_client
from app.routers import auth, transactions, model, analytics, insights, export, users

app = FastAPI(title="Expense AI API")

# Add test endpoint at startup
@app.on_event("startup")
async def startup_event():
    print("🚀 Backend starting up...")
    
    # Test database connection
    try:
        client = get_client()
        await client.admin.command("ping")
        print("✅ Database connected successfully")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
    
    print(f"📊 Backend ready on port 8005")
    print(f"🔗 API docs: http://localhost:8005/docs")

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(transactions.router, prefix="/api/transactions", tags=["transactions"])
app.include_router(model.router, prefix="/api/model", tags=["model"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(insights.router, prefix="/api/insights", tags=["insights"])
app.include_router(export.router, prefix="/api/export", tags=["export"])
app.include_router(users.router, tags=["users"])

# Serve uploaded avatars
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


@app.get("/api/health")
def health():
    return {"status": "ok"}
