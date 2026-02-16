import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class UserSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    avatar_url: HttpUrl | None = None


class UpdateEmailRequest(BaseModel):
    new_email: EmailStr


class UpdateUserPreferencesRequest(BaseModel):
    host_language: str | None = None
    theme: str | None = None


class UpdateUserNotificationsRequest(BaseModel):
    notifications: dict


class UpdatePasswordRequest(BaseModel):
    current_password: str = Field(..., max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


class TeamSettingsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    email: str
    full_name: str | None = None
    role: str
    created_at: str


class BillingInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    plan: str
    credits_balance: int
    stripe_customer_id: str | None = None
    stripe_subscription_id: str | None = None
