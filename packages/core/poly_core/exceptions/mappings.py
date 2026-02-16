"""
Mapping between ErrorCode enum and I18nKeys for localization.
"""

from typing import Dict

from poly_core.constants import I18nKeys

from .base import ErrorCode

# Map ErrorCode values to I18nKeys for localization
ERROR_CODE_TO_I18N_KEY: Dict[ErrorCode, I18nKeys] = {
    # Authentication errors
    ErrorCode.AUTH_INVALID_CREDENTIALS: I18nKeys.INVALID_CREDENTIALS,
    ErrorCode.AUTH_TOKEN_EXPIRED: I18nKeys.EXPIRED_REFRESH_TOKEN,
    ErrorCode.AUTH_TOKEN_INVALID: I18nKeys.INVALID_REFRESH_TOKEN,
    ErrorCode.AUTH_USER_NOT_FOUND: I18nKeys.USER_NOT_FOUND,
    ErrorCode.AUTH_EMAIL_NOT_VERIFIED: I18nKeys.EMAIL_NOT_VERIFIED,
    ErrorCode.AUTH_ACCOUNT_SUSPENDED: I18nKeys.ACCOUNT_SUSPENDED,
    ErrorCode.AUTH_INVALID_REFRESH_TOKEN: I18nKeys.INVALID_REFRESH_TOKEN,
    # Resource errors
    ErrorCode.RESOURCE_NOT_FOUND: I18nKeys.ERR_TEAMS_NOT_FOUND,
    # Team errors
    ErrorCode.AUTHZ_TEAM_ACCESS_DENIED: I18nKeys.ERR_AUTH_FORBIDDEN,
    # Job errors
    ErrorCode.BUSINESS_PLAN_LIMIT_REACHED: I18nKeys.ERR_JOBS_LIMIT_REACHED,
    ErrorCode.BUSINESS_JOB_QUEUE_FULL: I18nKeys.ERR_GENERIC_INTERNAL_ERROR,
    # Generic errors
    ErrorCode.GENERIC_FORBIDDEN: I18nKeys.ERR_AUTH_FORBIDDEN,
    ErrorCode.GENERIC_INTERNAL_ERROR: I18nKeys.ERR_GENERIC_INTERNAL_ERROR,
}


def get_i18n_key_for_error_code(error_code: ErrorCode) -> I18nKeys:
    """
    Get I18nKeys enum for a given ErrorCode.

    Args:
        error_code: ErrorCode enum value

    Returns:
        I18nKeys enum value for localization, or generic error if not found
    """
    return ERROR_CODE_TO_I18N_KEY.get(error_code, I18nKeys.ERR_GENERIC_INTERNAL_ERROR)
