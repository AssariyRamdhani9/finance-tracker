from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from typing import List, Optional
from app.models.schemas import TransactionCreate, TransactionResponse
from app.services.transaction_service import TransactionService
from app.services.ai_service import AIService
from app.core.security import verify_token
from app.core.config import settings
from supabase import create_client
import uuid
import os
from datetime import date
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/transactions", tags=["Transactions"])
transaction_service = TransactionService()
ai_service = AIService()


supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_SERVICE_ROLE_KEY
)

@router.get("/")
async def get_transactions(
    limit: int = 100,
    offset: int = 0,
    current_user: dict = Depends(verify_token)
):
    """Ambil semua transaksi user"""
    transactions = await transaction_service.get_transactions(
        current_user["user_id"],
        limit,
        offset
    )
    return transactions

@router.get("/month/{month}")
async def get_transactions_by_month(
    month: str,
    current_user: dict = Depends(verify_token)
):
    """Ambil transaksi bulan tertentu (format: 2026-07)"""
    transactions = await transaction_service.get_transactions_by_month(
        current_user["user_id"],
        month
    )
    return transactions

@router.post("/")
async def create_transaction(
    transaction: TransactionCreate,
    current_user: dict = Depends(verify_token)
):
    """Tambah transaksi baru (manual atau AI)"""
    data = transaction.dict()
    result = await transaction_service.create_transaction(
        current_user["user_id"],
        data
    )
    return result

@router.post("/scan-receipt")
async def scan_receipt(
    file: UploadFile = File(...),
    current_user: dict = Depends(verify_token)
):
    """Upload struk dan scan dengan AI"""
    
    logger.info(f"Received file: {file.filename}")
    

    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {ext} not allowed. Use: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    

    try:
        content = await file.read()
        file_size = len(content)
        if file_size > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
            )
        logger.info(f"File size: {file_size} bytes")
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")
    

    try:
        file_ext = ext[1:]  
        file_path = f"receipts/{current_user['user_id']}/{uuid.uuid4()}.{file_ext}"
        
        logger.info(f"Uploading to: {file_path}")
        

        upload_result = supabase.storage.from_("receipts").upload(
            file_path,
            content,
            {"content-type": file.content_type or "image/jpeg"}
        )
        
        logger.info(f"Upload result: {upload_result}")
        

        image_url = supabase.storage.from_("receipts").get_public_url(file_path)
        logger.info(f"Image URL: {image_url}")
        
    except Exception as e:
        logger.error(f"Storage upload error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload file to storage: {str(e)}"
        )
    

    try:
        if not settings.AI_ENABLED:
            ocr_result = {
                "merchant": "",
                "total": 0,
                "date": date.today().isoformat(),
                "items": [],
                "description": file.filename
            }
        else:
            ocr_result = await ai_service.ocr_receipt(image_url)
            logger.info(f"OCR result: {ocr_result}")
    except Exception as e:
        logger.error(f"OCR error: {e}")

        ocr_result = {
            "merchant": "",
            "total": 0,
            "date": date.today().isoformat(),
            "items": [],
            "description": file.filename
        }
    

    try:
        description = ocr_result.get("description", "") or ocr_result.get("merchant", "") or file.filename
        category_result = await ai_service.categorize_transaction(description)
        logger.info(f"Category result: {category_result}")
    except Exception as e:
        logger.error(f"Categorization error: {e}")
        category_result = {
            "category": "Lainnya",
            "confidence": 0,
            "is_ai": False
        }
    

    try:
        transaction_data = {
            "amount": ocr_result.get("total", 0),
            "description": description or "Transaksi dari struk",
            "merchant": ocr_result.get("merchant", ""),
            "category": category_result["category"],
            "transaction_date": ocr_result.get("date", date.today().isoformat()),
            "receipt_image_url": image_url,
            "is_ai_categorized": category_result.get("is_ai", False),
            "ai_confidence": category_result.get("confidence", 0)
        }
        
        result = await transaction_service.create_transaction(
            current_user["user_id"],
            transaction_data
        )
        
        logger.info(f"Transaction created: {result}")
        
    except Exception as e:
        logger.error(f"Create transaction error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create transaction: {str(e)}"
        )
    
    return {
        "transaction": result,
        "ocr": ocr_result,
        "category": category_result
    }

@router.patch("/{transaction_id}")
async def update_transaction(
    transaction_id: str,
    data: dict,
    current_user: dict = Depends(verify_token)
):
    """Update transaksi (misal: koreksi kategori)"""
    result = await transaction_service.update_transaction(
        current_user["user_id"],
        transaction_id,
        data
    )
    return result

@router.delete("/{transaction_id}")
async def delete_transaction(
    transaction_id: str,
    current_user: dict = Depends(verify_token)
):
    """Hapus transaksi"""
    success = await transaction_service.delete_transaction(
        current_user["user_id"],
        transaction_id
    )
    if not success:
        raise HTTPException(404, "Transaction not found")
    return {"message": "Transaction deleted"}

@router.get("/summary/{month}")
async def get_summary(
    month: str,
    current_user: dict = Depends(verify_token)
):
    """Ringkasan dashboard"""
    summary = await transaction_service.get_summary(
        current_user["user_id"],
        month
    )
    return summary