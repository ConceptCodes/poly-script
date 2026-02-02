import uuid

from pydantic import BaseModel, Field
from typing import Optional, List


class CompleteOnboardingRequest(BaseModel):
    team_name: str = Field(min_length=1, max_length=128)
    host_language: str = "en"
    plan: Optional[str] = None
    invite_emails: Optional[List[str]] = None


class OnboardingResponse(BaseModel):
    team_id: uuid.UUID
    name: str
    host_language: str
    plan: str
