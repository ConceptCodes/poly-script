from pydantic import BaseModel


class EngineCapabilitiesSchema(BaseModel):
    supports_timestamps: bool
    supports_diarization: bool
    supported_languages: list[str] | None = None


class EngineInfo(BaseModel):
    name: str
    capabilities: EngineCapabilitiesSchema


class EnginesResponse(BaseModel):
    engines: list[EngineInfo]
    default: str | None = None
