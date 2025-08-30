from fastapi import APIRouter

router = APIRouter()

@router.get("/sessions")
async def get_sessions():
    return {"active_sessions": [], "total_sessions": 0}