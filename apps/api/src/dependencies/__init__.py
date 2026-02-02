# Dependencies for API routes
from .dependencies import (
    get_locale,
    get_notification_service,
    get_auth_service,
    get_current_user,
    get_current_user_id,
    get_current_team_id,
    get_admin_auth_service,
)

__all__ = [
    "get_locale",
    "get_notification_service",
    "get_auth_service",
    "get_current_user",
    "get_current_user_id",
    "get_current_team_id",
    "get_admin_auth_service",
]
