import uuid
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


class UserSettingsResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    is_verified: bool
    is_active: bool
    created_at: str


class UpdateUserProfileRequest(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=128)
    avatar_url: Optional[str] = None


class UpdateEmailRequest(BaseModel):
    new_email: EmailStr


class UpdatePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(min_length=8, max_length=128)


class TeamSettingsResponse(BaseModel):
    id: uuid.UUID
    name: str
    host_language: str
    plan: str
    credits_balance: int
    created_at: str
    members_count: int


class UpdateTeamSettingsRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    host_language: Optional[str] = None


class TeamMemberItem(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email: str
    full_name: Optional[str] = None
    role: str
    created_at: str


class BillingInfoResponse(BaseModel):
    plan: str
    credits_balance: int
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
