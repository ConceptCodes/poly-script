import uuid

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str = Field(min_length=1, max_length=128)


class SignupResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    email: str
    full_name: str
    is_verified: bool


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class TokenResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., max_length=512)


class LogoutRequest(BaseModel):
    refresh_token: str = Field(..., max_length=512)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    full_name: str
    is_verified: bool
    is_active: bool
    is_suspended: bool
    created_at: str


class ResendVerificationRequest(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    token: str = Field(..., max_length=512)


class VerifyEmailCodeRequest(BaseModel):
    code: str = Field(min_length=6, max_length=6)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(..., max_length=512)
    new_password: str = Field(min_length=8, max_length=128)


class OAuthAuthURLRequest(BaseModel):
    redirect_url: HttpUrl | None = None
    state: str | None = None
    code_challenge: str | None = None
    code_challenge_method: str | None = None


class OAuthCallbackRequest(BaseModel):
    code: str = Field(..., max_length=128)
    state: str | None = None
    code_verifier: str | None = None
