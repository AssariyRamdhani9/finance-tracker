from pydantic import BaseModel, EmailStr
from datetime import date, datetime
from typing import Optional, List
from decimal import Decimal

# ─── AUTH ───

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

# ─── TRANSACTIONS ───

class TransactionCreate(BaseModel):
    amount: float
    description: str
    category: Optional[str] = None
    transaction_date: Optional[date] = None
    merchant: Optional[str] = None
    receipt_image_url: Optional[str] = None

class TransactionResponse(BaseModel):
    id: str
    user_id: str
    amount: float
    description: str
    category: str
    merchant: Optional[str]
    transaction_date: date
    receipt_image_url: Optional[str]
    is_ai_categorized: bool
    ai_confidence: Optional[float]
    created_at: datetime

# ─── BUDGET ───

class BudgetCreate(BaseModel):
    category: str
    monthly_limit: float
    month: str  # Format: YYYY-MM

class BudgetResponse(BaseModel):
    id: str
    user_id: str
    category: str
    monthly_limit: float
    month: str
    spent: float
    remaining: float
    percentage: float

# ─── INSIGHT ───

class InsightResponse(BaseModel):
    id: str
    content: str
    type: str  # weekly / monthly
    period_start: date
    period_end: date
    generated_at: datetime

# ─── AI ───

class OCRResult(BaseModel):
    merchant: str
    total: float
    date: date
    items: List[str]
    description: str

class CategoryResult(BaseModel):
    category: str
    confidence: float
    is_ai: bool