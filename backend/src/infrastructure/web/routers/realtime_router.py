from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def stream_status():
    return {"streaming": "active", "connections": 0}