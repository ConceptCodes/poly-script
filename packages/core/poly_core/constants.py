from enum import Enum, StrEnum
from typing import TypedDict


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
    uploads_per_month: int | float
    languages: int
    members: int | float


PLAN_LIMITS: dict[PlanType, PlanLimits] = {
    PlanType.FREE: {"uploads_per_month": 5, "languages": 2, "members": 1},
    PlanType.STANDARD: {"uploads_per_month": 25, "languages": 5, "members": 5},
    PlanType.PRO: {"uploads_per_month": float("inf"), "languages": 5, "members": float("inf")},
}

SUPPORTED_LANGUAGES = ["en", "de", "es", "fr", "jp"]

PLAN_STRIPE_IDS: dict[PlanType, str] = {
    PlanType.STANDARD: "price_standard_monthly",
    PlanType.PRO: "price_pro_monthly",
}

CREDIT_PRICE_CENTS = 100
CREDIT_BUNDLES: list[int] = [10, 50, 100]


class I18nKeys(StrEnum):
    # ============================================================================
    # LEGACY ERROR CODES (Backward Compatibility)
    # These are kept for backward compatibility. New code should use ERR_* variants.
    # ============================================================================
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

    TEAM_NOT_FOUND = "errors.teams.not_found"
    MEMBER_NOT_FOUND = "errors.teams.member_not_found"
    INVITATION_NOT_FOUND = "errors.teams.invitation_not_found"
    INVALID_INVITATION_TOKEN = "errors.teams.invalid_invitation_token"

    NOTIFICATION_INVITATION_SUBJECT = "notifications.invitation_subject"

    # ============================================================================
    # STANDARDIZED ERROR CODES (Error Code Taxonomy)
    # Pattern: ERR_{CATEGORY}_{SPECIFIC_ERROR}
    # Total: 71 error codes organized by category
    # ============================================================================

    # ----------------------------------------------------------------------------
    # AUTHENTICATION ERRORS (401, 403, 400, 409)
    # ----------------------------------------------------------------------------
    ERR_AUTH_INVALID_CREDENTIALS = "errors.auth.invalid_credentials"
    ERR_AUTH_USER_NOT_FOUND = "errors.auth.user_not_found"
    ERR_AUTH_EMAIL_ALREADY_EXISTS = "errors.auth.email_already_exists"
    ERR_AUTH_EMAIL_NOT_VERIFIED = "errors.auth.email_not_verified"
    ERR_AUTH_EMAIL_ALREADY_VERIFIED = "errors.auth.email_already_verified"
    ERR_AUTH_ACCOUNT_SUSPENDED = "errors.auth.account_suspended"
    ERR_AUTH_ACCOUNT_INACTIVE = "errors.auth.account_inactive"
    ERR_AUTH_INVALID_TOKEN = "errors.auth.invalid_token"
    ERR_AUTH_EXPIRED_TOKEN = "errors.auth.expired_token"
    ERR_AUTH_INVALID_VERIFICATION_TOKEN = "errors.auth.invalid_verification_token"
    ERR_AUTH_EXPIRED_VERIFICATION_TOKEN = "errors.auth.expired_verification_token"
    ERR_AUTH_INVALID_PASSWORD_RESET_TOKEN = "errors.auth.invalid_password_reset_token"
    ERR_AUTH_EXPIRED_PASSWORD_RESET_TOKEN = "errors.auth.expired_password_reset_token"
    ERR_AUTH_ALREADY_USED_PASSWORD_RESET_TOKEN = "errors.auth.already_used_password_reset_token"
    ERR_AUTH_INVALID_REFRESH_TOKEN = "errors.auth.invalid_refresh_token"
    ERR_AUTH_EXPIRED_REFRESH_TOKEN = "errors.auth.expired_refresh_token"
    ERR_AUTH_FORBIDDEN = "errors.auth.forbidden"
    ERR_AUTH_OAUTH_ERROR = "errors.auth.oauth_error"

    # ----------------------------------------------------------------------------
    # JOB ERRORS (404, 429, 400, 409, 413)
    # ----------------------------------------------------------------------------
    ERR_JOBS_NOT_FOUND = "errors.jobs.not_found"
    ERR_JOBS_LIMIT_REACHED = "errors.jobs.limit_reached"
    ERR_JOBS_UNSUPPORTED_LANGUAGE = "errors.jobs.unsupported_language"
    ERR_JOBS_INVALID_AUDIO = "errors.jobs.invalid_audio"
    ERR_JOBS_FILE_TOO_LARGE = "errors.jobs.file_too_large"
    ERR_JOBS_DOWNLOAD_FAILED = "errors.jobs.download_failed"
    ERR_JOBS_ALREADY_CANCELLED = "errors.jobs.already_cancelled"
    ERR_JOBS_CANNOT_CANCEL = "errors.jobs.cannot_cancel"

    # ----------------------------------------------------------------------------
    # TRANSCRIPT ERRORS (404, 409, 400, 500)
    # ----------------------------------------------------------------------------
    ERR_TRANSCRIPTS_NOT_FOUND = "errors.transcripts.not_found"
    ERR_TRANSCRIPTS_JOB_NOT_COMPLETE = "errors.transcripts.job_not_complete"
    ERR_TRANSCRIPTS_INVALID_SEGMENT = "errors.transcripts.invalid_segment"
    ERR_TRANSCRIPTS_EDIT_CONFLICT = "errors.transcripts.edit_conflict"
    ERR_TRANSCRIPTS_EXPORT_FAILED = "errors.transcripts.export_failed"
    ERR_TRANSCRIPTS_NO_HISTORY = "errors.transcripts.no_history"

    # ----------------------------------------------------------------------------
    # TEAM ERRORS (404, 429, 400, 409, 410, 403)
    # ----------------------------------------------------------------------------
    ERR_TEAMS_NOT_FOUND = "errors.teams.not_found"
    ERR_TEAMS_MEMBER_NOT_FOUND = "errors.teams.member_not_found"
    ERR_TEAMS_MEMBER_LIMIT_REACHED = "errors.teams.member_limit_reached"
    ERR_TEAMS_INVITATION_NOT_FOUND = "errors.teams.invitation_not_found"
    ERR_TEAMS_INVALID_INVITATION_TOKEN = "errors.teams.invalid_invitation_token"
    ERR_TEAMS_EXPIRED_INVITATION = "errors.teams.expired_invitation"
    ERR_TEAMS_ALREADY_MEMBER = "errors.teams.already_member"
    ERR_TEAMS_CANNOT_REMOVE_SELF = "errors.teams.cannot_remove_self"
    ERR_TEAMS_LAST_ADMIN = "errors.teams.last_admin"
    ERR_TEAMS_SUSPENDED = "errors.teams.suspended"

    # ----------------------------------------------------------------------------
    # BILLING ERRORS (402, 404, 400, 409, 502)
    # ----------------------------------------------------------------------------
    ERR_BILLING_PAYMENT_REQUIRED = "errors.billing.payment_required"
    ERR_BILLING_INVALID_PAYMENT_METHOD = "errors.billing.invalid_payment_method"
    ERR_BILLING_PAYMENT_FAILED = "errors.billing.payment_failed"
    ERR_BILLING_SUBSCRIPTION_NOT_FOUND = "errors.billing.subscription_not_found"
    ERR_BILLING_INVOICE_NOT_FOUND = "errors.billing.invoice_not_found"
    ERR_BILLING_CANNOT_DOWNGRADE = "errors.billing.cannot_downgrade"
    ERR_BILLING_ALREADY_SUBSCRIBED = "errors.billing.already_subscribed"
    ERR_BILLING_STRIPE_ERROR = "errors.billing.stripe_error"

    # ----------------------------------------------------------------------------
    # VALIDATION ERRORS (422)
    # ----------------------------------------------------------------------------
    ERR_VALIDATION_INVALID_INPUT = "errors.validation.invalid_input"
    ERR_VALIDATION_MISSING_FIELD = "errors.validation.missing_field"
    ERR_VALIDATION_INVALID_FORMAT = "errors.validation.invalid_format"
    ERR_VALIDATION_TOO_LONG = "errors.validation.too_long"
    ERR_VALIDATION_TOO_SHORT = "errors.validation.too_short"
    ERR_VALIDATION_INVALID_RANGE = "errors.validation.invalid_range"

    # ----------------------------------------------------------------------------
    # RATE LIMIT ERRORS (429)
    # ----------------------------------------------------------------------------
    ERR_RATE_LIMIT_EXCEEDED = "errors.rate_limit.exceeded"

    # ----------------------------------------------------------------------------
    # GENERIC/SYSTEM ERRORS (500, 501, 503, 504, 502)
    # ----------------------------------------------------------------------------
    ERR_GENERIC_INTERNAL_ERROR = "errors.generic.internal_error"
    ERR_GENERIC_SERVICE_UNAVAILABLE = "errors.generic.service_unavailable"
    ERR_GENERIC_NOT_IMPLEMENTED = "errors.generic.not_implemented"
    ERR_GENERIC_TIMEOUT = "errors.generic.timeout"
    ERR_GENERIC_DEPENDENCY_ERROR = "errors.generic.dependency_error"


# ================================================================================
# HTTP STATUS CODE MAPPING
# Maps each I18nKey to its corresponding HTTP status code per taxonomy
# ================================================================================

I18N_KEY_HTTP_STATUS: dict[I18nKeys, int] = {
    # ----------------------------------------------------------------------------
    # Legacy mappings (for backward compatibility)
    # ----------------------------------------------------------------------------
    I18nKeys.INVALID_CREDENTIALS: 401,
    I18nKeys.USER_NOT_FOUND: 401,
    I18nKeys.EMAIL_ALREADY_EXISTS: 409,
    I18nKeys.EMAIL_NOT_VERIFIED: 403,
    I18nKeys.EMAIL_ALREADY_VERIFIED: 400,
    I18nKeys.ACCOUNT_INACTIVE: 403,
    I18nKeys.ACCOUNT_SUSPENDED: 403,
    I18nKeys.INVALID_VERIFICATION_TOKEN: 400,
    I18nKeys.EXPIRED_VERIFICATION_TOKEN: 400,
    I18nKeys.INVALID_PASSWORD_RESET_TOKEN: 400,
    I18nKeys.EXPIRED_PASSWORD_RESET_TOKEN: 400,
    I18nKeys.ALREADY_USED_PASSWORD_RESET_TOKEN: 400,
    I18nKeys.INVALID_REFRESH_TOKEN: 401,
    I18nKeys.EXPIRED_REFRESH_TOKEN: 401,
    I18nKeys.TEAM_NOT_FOUND: 404,
    I18nKeys.MEMBER_NOT_FOUND: 404,
    I18nKeys.INVITATION_NOT_FOUND: 404,
    I18nKeys.INVALID_INVITATION_TOKEN: 400,
    # ----------------------------------------------------------------------------
    # Auth errors (401, 403, 400, 409)
    # ----------------------------------------------------------------------------
    I18nKeys.ERR_AUTH_INVALID_CREDENTIALS: 401,
    I18nKeys.ERR_AUTH_USER_NOT_FOUND: 401,
    I18nKeys.ERR_AUTH_EMAIL_ALREADY_EXISTS: 409,
    I18nKeys.ERR_AUTH_EMAIL_NOT_VERIFIED: 403,
    I18nKeys.ERR_AUTH_EMAIL_ALREADY_VERIFIED: 400,
    I18nKeys.ERR_AUTH_ACCOUNT_SUSPENDED: 403,
    I18nKeys.ERR_AUTH_ACCOUNT_INACTIVE: 403,
    I18nKeys.ERR_AUTH_INVALID_TOKEN: 401,
    I18nKeys.ERR_AUTH_EXPIRED_TOKEN: 401,
    I18nKeys.ERR_AUTH_INVALID_VERIFICATION_TOKEN: 400,
    I18nKeys.ERR_AUTH_EXPIRED_VERIFICATION_TOKEN: 400,
    I18nKeys.ERR_AUTH_INVALID_PASSWORD_RESET_TOKEN: 400,
    I18nKeys.ERR_AUTH_EXPIRED_PASSWORD_RESET_TOKEN: 400,
    I18nKeys.ERR_AUTH_ALREADY_USED_PASSWORD_RESET_TOKEN: 400,
    I18nKeys.ERR_AUTH_INVALID_REFRESH_TOKEN: 401,
    I18nKeys.ERR_AUTH_EXPIRED_REFRESH_TOKEN: 401,
    I18nKeys.ERR_AUTH_FORBIDDEN: 403,
    I18nKeys.ERR_AUTH_OAUTH_ERROR: 400,
    # ----------------------------------------------------------------------------
    # Job errors (404, 429, 400, 409, 413)
    # ----------------------------------------------------------------------------
    I18nKeys.ERR_JOBS_NOT_FOUND: 404,
    I18nKeys.ERR_JOBS_LIMIT_REACHED: 429,
    I18nKeys.ERR_JOBS_UNSUPPORTED_LANGUAGE: 400,
    I18nKeys.ERR_JOBS_INVALID_AUDIO: 400,
    I18nKeys.ERR_JOBS_FILE_TOO_LARGE: 413,
    I18nKeys.ERR_JOBS_DOWNLOAD_FAILED: 400,
    I18nKeys.ERR_JOBS_ALREADY_CANCELLED: 409,
    I18nKeys.ERR_JOBS_CANNOT_CANCEL: 409,
    # ----------------------------------------------------------------------------
    # Transcript errors (404, 409, 400, 500)
    # ----------------------------------------------------------------------------
    I18nKeys.ERR_TRANSCRIPTS_NOT_FOUND: 404,
    I18nKeys.ERR_TRANSCRIPTS_JOB_NOT_COMPLETE: 409,
    I18nKeys.ERR_TRANSCRIPTS_INVALID_SEGMENT: 400,
    I18nKeys.ERR_TRANSCRIPTS_EDIT_CONFLICT: 409,
    I18nKeys.ERR_TRANSCRIPTS_EXPORT_FAILED: 500,
    I18nKeys.ERR_TRANSCRIPTS_NO_HISTORY: 404,
    # ----------------------------------------------------------------------------
    # Team errors (404, 429, 400, 409, 410, 403)
    # ----------------------------------------------------------------------------
    I18nKeys.ERR_TEAMS_NOT_FOUND: 404,
    I18nKeys.ERR_TEAMS_MEMBER_NOT_FOUND: 404,
    I18nKeys.ERR_TEAMS_MEMBER_LIMIT_REACHED: 429,
    I18nKeys.ERR_TEAMS_INVITATION_NOT_FOUND: 404,
    I18nKeys.ERR_TEAMS_INVALID_INVITATION_TOKEN: 400,
    I18nKeys.ERR_TEAMS_EXPIRED_INVITATION: 410,
    I18nKeys.ERR_TEAMS_ALREADY_MEMBER: 409,
    I18nKeys.ERR_TEAMS_CANNOT_REMOVE_SELF: 400,
    I18nKeys.ERR_TEAMS_LAST_ADMIN: 400,
    I18nKeys.ERR_TEAMS_SUSPENDED: 403,
    # ----------------------------------------------------------------------------
    # Billing errors (402, 404, 400, 409, 502)
    # ----------------------------------------------------------------------------
    I18nKeys.ERR_BILLING_PAYMENT_REQUIRED: 402,
    I18nKeys.ERR_BILLING_INVALID_PAYMENT_METHOD: 400,
    I18nKeys.ERR_BILLING_PAYMENT_FAILED: 402,
    I18nKeys.ERR_BILLING_SUBSCRIPTION_NOT_FOUND: 404,
    I18nKeys.ERR_BILLING_INVOICE_NOT_FOUND: 404,
    I18nKeys.ERR_BILLING_CANNOT_DOWNGRADE: 400,
    I18nKeys.ERR_BILLING_ALREADY_SUBSCRIBED: 409,
    I18nKeys.ERR_BILLING_STRIPE_ERROR: 502,
    # ----------------------------------------------------------------------------
    # Validation errors (422)
    # ----------------------------------------------------------------------------
    I18nKeys.ERR_VALIDATION_INVALID_INPUT: 422,
    I18nKeys.ERR_VALIDATION_MISSING_FIELD: 422,
    I18nKeys.ERR_VALIDATION_INVALID_FORMAT: 422,
    I18nKeys.ERR_VALIDATION_TOO_LONG: 422,
    I18nKeys.ERR_VALIDATION_TOO_SHORT: 422,
    I18nKeys.ERR_VALIDATION_INVALID_RANGE: 422,
    # ----------------------------------------------------------------------------
    # Rate limit errors (429)
    # ----------------------------------------------------------------------------
    I18nKeys.ERR_RATE_LIMIT_EXCEEDED: 429,
    # ----------------------------------------------------------------------------
    # Generic/system errors (500, 501, 503, 504, 502)
    # ----------------------------------------------------------------------------
    I18nKeys.ERR_GENERIC_INTERNAL_ERROR: 500,
    I18nKeys.ERR_GENERIC_SERVICE_UNAVAILABLE: 503,
    I18nKeys.ERR_GENERIC_NOT_IMPLEMENTED: 501,
    I18nKeys.ERR_GENERIC_TIMEOUT: 504,
    I18nKeys.ERR_GENERIC_DEPENDENCY_ERROR: 502,
}


def get_error_status_code(i18n_key: I18nKeys) -> int:
    """Get the HTTP status code for a given I18nKey.

    Args:
        i18n_key: The I18nKeys enum value representing the error

    Returns:
        int: The HTTP status code (e.g., 400, 401, 404, 500)

    Raises:
        KeyError: If the i18n_key is not found in the mapping

    Example:
        >>> get_error_status_code(I18nKeys.ERR_AUTH_INVALID_CREDENTIALS)
        401
        >>> get_error_status_code(I18nKeys.ERR_JOBS_NOT_FOUND)
        404
        >>> get_error_status_code(I18nKeys.ERR_JOBS_LIMIT_REACHED)
        429
    """
    return I18N_KEY_HTTP_STATUS[i18n_key]
