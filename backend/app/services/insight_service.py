from app.services.ai_service import AIService
from app.services.transaction_service import TransactionService
from app.core.config import settings
from supabase import create_client
from datetime import datetime, timedelta, date
from typing import List, Dict
import json

class InsightService:
    def __init__(self):
        self.supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.ai_service = AIService()
        self.transaction_service = TransactionService()
    
    async def generate_insights(self, user_id: str) -> List[Dict]:
        """Generate insight untuk user"""
        

        current_month = date.today().strftime("%Y-%m")
        transactions = await self.transaction_service.get_transactions_by_month(user_id, current_month)
        

        budgets = await self.get_budgets(user_id, current_month)
        

        insight_text = await self.ai_service.generate_insights(transactions, budgets)
        

        insight_data = {
            "user_id": user_id,
            "content": insight_text,
            "type": "monthly",
            "period_start": f"{current_month}-01",
            "period_end": date.today().isoformat(),
            "generated_at": datetime.now().isoformat()
        }
        
        response = self.supabase.table("insights")\
            .insert(insight_data)\
            .execute()
        
        return response.data if response.data else []
    
    async def get_insights(self, user_id: str, limit: int = 5) -> List[Dict]:
        """Ambil insight terbaru"""
        response = self.supabase.table("insights")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("generated_at", desc=True)\
            .limit(limit)\
            .execute()
        
        return response.data
    
    async def get_budgets(self, user_id: str, month: str) -> List[Dict]:
        """Ambil budget user"""
        response = self.supabase.table("budgets")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("month", f"{month}-01")\
            .execute()
        
        return response.data