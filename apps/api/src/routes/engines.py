from fastapi import APIRouter
from poly_stt import EngineRegistry

router = APIRouter()

@router.get("/v1/engines")
async def list_engines():
    return {
        "engines": EngineRegistry.list_engines(),
        "default": EngineRegistry._default,
    }