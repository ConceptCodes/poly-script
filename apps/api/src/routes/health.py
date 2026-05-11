from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/v1/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now(UTC).isoformat()}


health_router = router
health_router = router
