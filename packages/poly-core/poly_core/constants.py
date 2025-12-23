from typing import Dict, Any, Union, TypedDict

# Plan Limits
class PlanLimits(TypedDict):
    uploads_per_month: Union[int, float]
    languages: int
    members: Union[int, float]

PLAN_LIMITS: Dict[str, PlanLimits] = {
    "FREE": {
        "uploads_per_month": 5,
        "languages": 2,
        "members": 1
    },
    "STANDARD": {
        "uploads_per_month": 25,
        "languages": 5,
        "members": 5
    },
    "PRO": {
        "uploads_per_month": float('inf'),
        "languages": 5,
        "members": float('inf')
    },
}

# Stripe Product/Price IDs (These should be replaced by actual IDs from Stripe Dashboard)
PLAN_STRIPE_IDS = {
    "STANDARD": "price_standard_monthly",
    "PRO": "price_pro_monthly",
}

# Credit Pricing (e.g., $10 for 10 credits)
CREDIT_PRICE_CENTS = 1000
CREDIT_AMOUNT = 10

# I18n Keys
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
