from fastapi import APIRouter

router = APIRouter()

@router.get("/metrics")
async def get_metrics():
    return {"cpu_usage": 45.2, "memory_usage": 2048, "active_analyses": 3}