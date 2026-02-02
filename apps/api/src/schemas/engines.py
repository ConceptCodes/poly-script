from typing import Optional, List
from pydantic import BaseModel


class EngineCapabilitiesSchema(BaseModel):
    supports_timestamps: bool
    supports_diarization: bool
    supported_languages: Optional[List[str]] = None


class EngineInfo(BaseModel):
    name: str
    capabilities: EngineCapabilitiesSchema


class EnginesResponse(BaseModel):
    engines: List[EngineInfo]
    default: Optional[str] = None
