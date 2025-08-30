from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def ml_status():
    return {"ml_services": "available", "models_loaded": 3}