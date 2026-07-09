
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from app.models.schemas import BudgetCreate, BudgetResponse
from app.core.security import verify_token
from app.core.config import settings
from supabase import create_client
from datetime import date

router = APIRouter(prefix="/budgets", tags=["Budgets"])
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)

@router.get("/")
async def get_budgets(current_user: dict = Depends(verify_token)):
    """Ambil semua budget user"""
    response = supabase.table("budgets")\
        .select("*")\
        .eq("user_id", current_user["user_id"])\
        .execute()
    
    return response.data

@router.get("/month/{month}")
async def get_budgets_by_month(
    month: str,
    current_user: dict = Depends(verify_token)
):
    """Ambil budget bulan tertentu"""
    response = supabase.table("budgets")\
        .select("*")\
        .eq("user_id", current_user["user_id"])\
        .eq("month", f"{month}-01")\
        .execute()
    
    return response.data

@router.post("/")
async def create_budget(
    budget: BudgetCreate,
    current_user: dict = Depends(verify_token)
):
    """Buat budget baru"""
    
    data = budget.dict()
    data["user_id"] = current_user["user_id"]
    
  
    existing = supabase.table("budgets")\
        .select("*")\
        .eq("user_id", current_user["user_id"])\
        .eq("category", data["category"])\
        .eq("month", data["month"])\
        .execute()
    
    if existing.data:
        raise HTTPException(400, f"Budget untuk {data['category']} bulan ini sudah ada")
    
    response = supabase.table("budgets")\
        .insert(data)\
        .execute()
    
    return response.data[0] if response.data else None

@router.get("/status")
async def get_budget_status(current_user: dict = Depends(verify_token)):
    """Status budget vs pengeluaran aktual"""
    

    budgets_res = supabase.table("budgets")\
        .select("*")\
        .eq("user_id", current_user["user_id"])\
        .execute()
    
    if not budgets_res.data:
        return []
    

    today = date.today()
    start_date = date(today.year, today.month, 1)
    
    if today.month == 12:
        end_date = date(today.year + 1, 1, 1)
    else:
        end_date = date(today.year, today.month + 1, 1)
    
    transactions_res = supabase.table("transactions")\
        .select("*")\
        .eq("user_id", current_user["user_id"])\
        .gte("transaction_date", start_date.isoformat())\
        .lt("transaction_date", end_date.isoformat())\
        .execute()
    

    spent = {}
    for t in transactions_res.data:
        cat = t.get("category", "Lainnya")
        spent[cat] = spent.get(cat, 0) + float(t.get("amount", 0))
    

    result = []
    for b in budgets_res.data:
        category = b["category"]
        limit = float(b["monthly_limit"])
        actual = spent.get(category, 0)
        remaining = limit - actual
        percentage = (actual / limit * 100) if limit > 0 else 0
        
        result.append({
            "id": b["id"],
            "user_id": b["user_id"],
            "category": category,
            "monthly_limit": limit,
            "spent": actual,
            "remaining": remaining,
            "percentage": min(percentage, 100),
            "is_overbudget": actual > limit
        })
    
    return result
@router.delete("/{budget_id}")
async def delete_budget(
    budget_id: str,
    current_user: dict = Depends(verify_token)
):
    """Hapus budget"""
    response = supabase.table("budgets")\
        .delete()\
        .eq("id", budget_id)\
        .eq("user_id", current_user["user_id"])\
        .execute()
    
    if not response.data:
        raise HTTPException(404, "Budget not found")
    
    return {"message": "Budget deleted"}