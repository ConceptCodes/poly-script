# Dependencies for API routes
from poly_db.database import get_db_session

from .dependencies import (
    get_admin_auth_service,
    get_async_auth_service,
    get_async_db,
    get_auth_service,
    get_current_admin,
    get_current_team_id,
    get_current_user,
    get_current_user_id,
    get_locale,
    get_notification_service,
    get_team_context,
)

__all__ = [
    "get_admin_auth_service",
    "get_async_auth_service",
    "get_async_db",
    "get_auth_service",
    "get_current_admin",
    "get_current_team_id",
    "get_current_user",
    "get_current_user_id",
    "get_db_session",
    "get_locale",
    "get_notification_service",
    "get_team_context",
]
