# backend/app/routers/auth.py

from fastapi import APIRouter, HTTPException, status, Depends
from app.models.schemas import UserRegister, UserLogin, TokenResponse
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from supabase import create_client
import datetime

router = APIRouter(prefix="/auth", tags=["Authentication"])


supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

@router.post("/register")
async def register(user_data: UserRegister):
    print(f"EMAIL RECEIVED: {repr(user_data.email)}")
    try:
        response = supabase.auth.sign_up({
            "email": user_data.email,
            "password": user_data.password,
            "options": {
                "data": {
                    "name": user_data.name or user_data.email.split("@")[0]
                }
            }
        })
        
        if not response.user:
            raise HTTPException(status_code=400, detail="Registration failed")
        
        return {
            "message": "User registered successfully",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "name": response.user.user_metadata.get("name", "")
            }
        }
    except Exception as e:
        print(f"REGISTER ERROR: {repr(e)}")   
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    try:

        response = supabase.auth.sign_in_with_password({
            "email": user_data.email,
            "password": user_data.password
        })
        
        if not response.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        

        access_token = create_access_token(
            data={
                "sub": response.user.id,
                "email": response.user.email
            }
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "name": response.user.user_metadata.get("name", "")
            }
        }
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/logout")
async def logout():
    return {"message": "Logged out successfully"}