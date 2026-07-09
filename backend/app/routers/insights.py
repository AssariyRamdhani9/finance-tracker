from fastapi import APIRouter, Depends, HTTPException
from app.services.insight_service import InsightService
from app.core.security import verify_token
from app.core.config import settings

router = APIRouter(prefix="/insights", tags=["Insights"])
insight_service = InsightService()

@router.get("/")
async def get_insights(
    limit: int = 5,
    current_user: dict = Depends(verify_token)
):
    """Ambil insight terbaru"""
    insights = await insight_service.get_insights(
        current_user["user_id"],
        limit
    )
    return insights

@router.post("/generate")
async def generate_insights(current_user: dict = Depends(verify_token)):
    """Generate insight baru"""
    if not settings.AI_ENABLED:
        return {"message": "AI features are disabled. Enable in settings."}
    
    insights = await insight_service.generate_insights(current_user["user_id"])
    return insights