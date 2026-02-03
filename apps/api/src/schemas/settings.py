import uuid

from pydantic import BaseModel, EmailStr, Field


class UserSettingsResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str | None = None
    is_verified: bool
    is_active: bool
    created_at: str
    host_language: str
    theme: str
    notifications: dict


class UpdateUserProfileRequest(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=128)
    avatar_url: str | None = None


class UpdateEmailRequest(BaseModel):
    new_email: EmailStr


class UpdateUserPreferencesRequest(BaseModel):
    host_language: str | None = None
    theme: str | None = None


class UpdateUserNotificationsRequest(BaseModel):
    notifications: dict


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
    name: str | None = Field(None, min_length=1, max_length=128)
    host_language: str | None = None


class TeamMemberItem(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    email: str
    full_name: str | None = None
    role: str
    created_at: str


class BillingInfoResponse(BaseModel):
    plan: str
    credits_balance: int
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
