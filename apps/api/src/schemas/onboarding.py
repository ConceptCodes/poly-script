import uuid

from pydantic import BaseModel, ConfigDict, Field


class CompleteOnboardingRequest(BaseModel):
    team_name: str = Field(min_length=1, max_length=128)
    host_language: str = Field("en", max_length=10)
    plan: str | None = None
    invite_emails: list[str] | None = None


class OnboardingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    team_id: uuid.UUID
    name: str
    host_language: str
    plan: str
