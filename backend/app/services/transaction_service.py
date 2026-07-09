from app.services.ai_service import AIService
from app.core.config import settings
from supabase import create_client
from datetime import datetime, date, timedelta
from typing import List, Dict, Optional
import uuid

class TransactionService:
    def __init__(self):
        self.supabase = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY
        )
        self.ai_service = AIService()
    
    async def create_transaction(self, user_id: str, data: Dict) -> Dict:
        """Buat transaksi baru dengan AI categorization jika diperlukan"""
        

        if not data.get("category") and settings.AI_ENABLED:
            ai_result = await self.ai_service.categorize_transaction(
                data.get("description", "")
            )
            data["category"] = ai_result["category"]
            data["is_ai_categorized"] = ai_result.get("is_ai", False)
            data["ai_confidence"] = ai_result.get("confidence", 0)
        else:
            data["is_ai_categorized"] = False
            data["ai_confidence"] = None
        

        data["user_id"] = user_id
        if not data.get("transaction_date"):
            data["transaction_date"] = date.today().isoformat()
        elif isinstance(data["transaction_date"], (date, datetime)):
            data["transaction_date"] = data["transaction_date"].isoformat()
        

        response = self.supabase.table("transactions")\
            .insert(data)\
            .execute()
        
        return response.data[0] if response.data else None
    
    async def get_transactions(self, user_id: str, limit: int = 100, offset: int = 0) -> List[Dict]:
        """Ambil semua transaksi user"""
        response = self.supabase.table("transactions")\
            .select("*")\
            .eq("user_id", user_id)\
            .order("transaction_date", desc=True)\
            .range(offset, offset + limit - 1)\
            .execute()
        
        return response.data
    
    async def get_transactions_by_month(self, user_id: str, month: str) -> List[Dict]:
        """Ambil transaksi bulan tertentu (format: 2026-07)"""
        

        year, month_num = month.split('-')
        start_date = f"{year}-{month_num}-01"
        

        next_month = int(month_num) + 1
        next_year = int(year)
        if next_month > 12:
            next_month = 1
            next_year += 1
        end_date = f"{next_year:04d}-{next_month:02d}-01"
        
        response = self.supabase.table("transactions")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("transaction_date", start_date)\
            .lt("transaction_date", end_date)\
            .order("transaction_date", desc=True)\
            .execute()
        
        return response.data
    
    async def get_transactions_by_date_range(self, user_id: str, start_date: str, end_date: str) -> List[Dict]:
        """Ambil transaksi dalam rentang tanggal"""
        response = self.supabase.table("transactions")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("transaction_date", start_date)\
            .lte("transaction_date", end_date)\
            .order("transaction_date", desc=True)\
            .execute()
        
        return response.data
    
    async def update_transaction(self, user_id: str, transaction_id: str, data: Dict) -> Dict:
        """Update transaksi"""
        response = self.supabase.table("transactions")\
            .update(data)\
            .eq("id", transaction_id)\
            .eq("user_id", user_id)\
            .execute()
        
        return response.data[0] if response.data else None
    
    async def delete_transaction(self, user_id: str, transaction_id: str) -> bool:
        """Hapus transaksi"""
        response = self.supabase.table("transactions")\
            .delete()\
            .eq("id", transaction_id)\
            .eq("user_id", user_id)\
            .execute()
        
        return len(response.data) > 0
    
    async def get_summary(self, user_id: str, month: str) -> Dict:
        """Dapatkan ringkasan dashboard"""
        transactions = await self.get_transactions_by_month(user_id, month)
        
        total = 0
        by_category = {}
        by_day = {}
        
        for t in transactions:
            amount = float(t.get("amount", 0))
            category = t.get("category", "Lainnya")
            trans_date = t.get("transaction_date", "")
            
            total += amount
            by_category[category] = by_category.get(category, 0) + amount
            
            if trans_date:
                by_day[trans_date] = by_day.get(trans_date, 0) + amount
        
        return {
            "total": total,
            "count": len(transactions),
            "by_category": by_category,
            "by_day": by_day,
            "average": total / len(transactions) if transactions else 0
        }