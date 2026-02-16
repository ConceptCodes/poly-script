from pydantic import BaseModel, ConfigDict


class EngineCapabilitiesSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    supports_timestamps: bool
    supports_diarization: bool
    supported_languages: list[str] | None = None


class EngineInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    capabilities: EngineCapabilitiesSchema


class EnginesResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    engines: list[EngineInfo]
    default: str | None = None
