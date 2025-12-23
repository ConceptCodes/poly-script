from fastapi import APIRouter
from datetime import datetime, timezone

router = APIRouter()

@router.get("/v1/health")
async def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
