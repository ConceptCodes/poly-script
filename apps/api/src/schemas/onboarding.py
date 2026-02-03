import uuid

from pydantic import BaseModel, Field


class CompleteOnboardingRequest(BaseModel):
    team_name: str = Field(min_length=1, max_length=128)
    host_language: str = "en"
    plan: str | None = None
    invite_emails: list[str] | None = None


class OnboardingResponse(BaseModel):
    team_id: uuid.UUID
    name: str
    host_language: str
    plan: str
