from enum import Enum
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
    PlanType.FREE: {
        "uploads_per_month": 5,
        "languages": 2,
        "members": 1
    },
    PlanType.STANDARD: {
        "uploads_per_month": 25,
        "languages": 5,
        "members": 5
    },
    PlanType.PRO: {
        "uploads_per_month": float('inf'),
        "languages": 5,
        "members": float('inf')
    },
}

PLAN_STRIPE_IDS: dict[PlanType, str] = {
    PlanType.STANDARD: "price_standard_monthly",
    PlanType.PRO: "price_pro_monthly",
}

CREDIT_PRICE_CENTS = 1000
CREDIT_AMOUNT = 10


class I18nKeys:
    ERR_AUTH_INVALID_CREDENTIALS = "errors.auth.invalid_credentials"
    ERR_AUTH_USER_NOT_FOUND = "errors.auth.user_not_found"
    ERR_AUTH_EMAIL_ALREADY_EXISTS = "errors.auth.email_already_exists"
    ERR_AUTH_NOT_VERIFIED = "errors.auth.not_verified"

    ERR_JOBS_NOT_FOUND = "errors.jobs.not_found"
    ERR_JOBS_LIMIT_REACHED = "errors.jobs.limit_reached"
    ERR_JOBS_UNSUPPORTED_LANGUAGE = "errors.jobs.unsupported_language"

    ERR_GENERIC_INTERNAL_ERROR = "errors.generic.internal_error"
    ERR_GENERIC_FORBIDDEN = "errors.generic.forbidden"

    ERR_TEAM_NOT_FOUND = "errors.teams.not_found"

    NOTIF_INVITATION_SUBJECT = "notifications.invitation_subject"
