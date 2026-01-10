from enum import Enum, StrEnum
from typing import Union, TypedDict


class JobState(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELED = "CANCELED"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"


class TeamRole(str, Enum):
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"


class PlanType(str, Enum):
    FREE = "FREE"
    STANDARD = "STANDARD"
    PRO = "PRO"


class PlanLimits(TypedDict):
    uploads_per_month: Union[int, float]
    languages: int
    members: Union[int, float]


PLAN_LIMITS: dict[PlanType, PlanLimits] = {
    PlanType.FREE: {"uploads_per_month": 5, "languages": 2, "members": 1},
    PlanType.STANDARD: {"uploads_per_month": 25, "languages": 5, "members": 5},
    PlanType.PRO: {"uploads_per_month": float("inf"), "languages": 5, "members": float("inf")},
}

PLAN_STRIPE_IDS: dict[PlanType, str] = {
    PlanType.STANDARD: "price_standard_monthly",
    PlanType.PRO: "price_pro_monthly",
}

CREDIT_PRICE_CENTS = 100
CREDIT_AMOUNT = 10


class I18nKeys(StrEnum):
    INVALID_CREDENTIALS = "errors.auth.invalid_credentials"
    USER_NOT_FOUND = "errors.auth.user_not_found"
    EMAIL_ALREADY_EXISTS = "errors.auth.email_already_exists"
    EMAIL_NOT_VERIFIED = "errors.auth.not_verified"
    EMAIL_ALREADY_VERIFIED = "errors.auth.email_already_verified"
    ACCOUNT_INACTIVE = "errors.auth.account_inactive"
    ACCOUNT_SUSPENDED = "errors.auth.account_suspended"

    INVALID_VERIFICATION_TOKEN = "errors.auth.invalid_verification_token"
    EXPIRED_VERIFICATION_TOKEN = "errors.auth.expired_verification_token"
    INVALID_PASSWORD_RESET_TOKEN = "errors.auth.invalid_password_reset_token"
    EXPIRED_PASSWORD_RESET_TOKEN = "errors.auth.expired_password_reset_token"
    ALREADY_USED_PASSWORD_RESET_TOKEN = "errors.auth.already_used_password_reset_token"
    INVALID_REFRESH_TOKEN = "errors.auth.invalid_refresh_token"
    EXPIRED_REFRESH_TOKEN = "errors.auth.expired_refresh_token"

    ERR_JOBS_NOT_FOUND = "errors.jobs.not_found"
    ERR_JOBS_LIMIT_REACHED = "errors.jobs.limit_reached"
    ERR_JOBS_UNSUPPORTED_LANGUAGE = "errors.jobs.unsupported_language"

    ERR_GENERIC_INTERNAL_ERROR = "errors.generic.internal_error"
    ERR_GENERIC_FORBIDDEN = "errors.generic.forbidden"

    TEAM_NOT_FOUND = "errors.teams.not_found"
    ERR_TEAM_NOT_FOUND = "errors.teams.not_found"
    MEMBER_NOT_FOUND = "errors.teams.member_not_found"
    INVITATION_NOT_FOUND = "errors.teams.invitation_not_found"
    INVALID_INVITATION_TOKEN = "errors.teams.invalid_invitation_token"

    NOTIFICATION_INVITATION_SUBJECT = "notifications.invitation_subject"
