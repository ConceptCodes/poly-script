from typing import TypedDict, Required, NotRequired


class JWTTokenPayload(TypedDict):
    sub: str  # user_id as string
    exp: int  # expiration timestamp
    iat: int  # issued at timestamp


class TokenResponse(TypedDict):
    access_token: Required[str]
    refresh_token: Required[str]


class RefreshTokenResponse(TypedDict):
    access_token: Required[str]
    refresh_token: Required[str]


class GoogleUserInfo(TypedDict):
    google_id: Required[str]
    email: Required[str]
    full_name: Required[str]
    access_token: Required[str]
    refresh_token: Required[str]
    expires_at: NotRequired[str | None]


class EmailTemplateContext(TypedDict, total=False):
    user_name: NotRequired[str]
    verification_url: NotRequired[str]
    reset_url: NotRequired[str]
    invitee_name: NotRequired[str]
    inviter_name: NotRequired[str]
    team_name: NotRequired[str]
    accept_url: NotRequired[str]
    role: NotRequired[str]


class TeamMemberLimits(TypedDict):
    max_members: int
    max_upload_mb: int
    max_jobs_per_month: int
