from fastapi import APIRouter
from poly_stt import EngineRegistry
from src.schemas.engines import EnginesResponse, EngineInfo, EngineCapabilitiesSchema

router = APIRouter()

@router.get("/v1/engines", response_model=EnginesResponse)
async def list_engines():
    engines = []
    for engine in EngineRegistry.list_engines():
        capabilities = engine["capabilities"]
        engines.append(
            EngineInfo(
                name=engine["name"],
                capabilities=EngineCapabilitiesSchema(
                    supports_timestamps=capabilities.supports_timestamps,
                    supports_diarization=capabilities.supports_diarization,
                    supported_languages=capabilities.supported_languages,
                ),
            )
        )
    return {
        "engines": engines,
        "default": EngineRegistry._default,
    }
