from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, transactions, budgets, insights, export
from app.core.config import settings

app = FastAPI(
    title="Finance Tracker API",
    description="AI-Powered Personal Finance Tracker",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(insights.router)
app.include_router(export.router)

@app.get("/")
async def root():
    return {
        "message": "Finance Tracker API",
        "version": "1.0.0",
        "ai_enabled": settings.AI_ENABLED,
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Run with: uvicorn app.main:app --reload