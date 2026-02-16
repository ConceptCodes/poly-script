from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from poly_core.services.admin_auth import AdminAuthService
from poly_core.services.auth import AuthService
from poly_core.services.auth_async import AsyncAuthService
from poly_core.services.notification import NotificationService
from poly_db.database import get_db_session
from poly_db.models.teams import Team
from poly_db.repositories import AdminUserRepository, TeamMemberRepository, UserRepository
from src.config import get_settings

if TYPE_CHECKING:
    from sqlalchemy.orm import Session


async def get_locale(accept_language: str | None = Header(None)) -> str:
    """
    Parse Accept-Language header and return the best matching locale.
    Simple implementation: take the first language from the header.
    Authentication dependency will overload this to prefer user profile settings.
    """
    if not accept_language:
        return "en"

    # Basic parsing: "en-US,en;q=0.9" -> "en"
    # We just want the primary tag of the first preference
    primary = accept_language.split(",")[0].strip().split(";")[0].strip()

    # Handle "en-US" -> "en" if strict match fails (simplified for now)
    # The i18n service handles fallback to 'en', so we just return the code.
    return primary


def _parse_expiry_to_minutes(expiry: str) -> int:
    value = expiry.strip().lower()
    if value.endswith("h"):
        return int(value[:-1]) * 60
    if value.endswith("m"):
        return int(value[:-1])
    if value.endswith("d"):
        return int(value[:-1]) * 24 * 60
    return int(value)


def get_notification_service() -> NotificationService:
    settings = get_settings()
    templates_dir = Path(__file__).resolve().parent / "templates"
    return NotificationService(
        smtp_host=settings.SMTP_HOST,
        smtp_port=settings.SMTP_PORT,
        smtp_user=settings.SMTP_USER,
        smtp_password=settings.SMTP_PASSWORD,
        smtp_from=settings.SMTP_FROM,
        templates_dir=str(templates_dir),
        app_url=settings.APP_URL,
    )


def get_auth_service(db: Session = Depends(get_db_session)) -> AuthService:
    settings = get_settings()
    notification_service = get_notification_service()
    return AuthService(
        db_session=db,
        jwt_secret=settings.JWT_SECRET,
        jwt_expiry_minutes=_parse_expiry_to_minutes(settings.JWT_EXPIRY),
        notification_service=notification_service,
        email_verification_expiry_hours=settings.EMAIL_VERIFICATION_EXPIRY,
        password_reset_expiry_hours=settings.PASSWORD_RESET_EXPIRY,
    )


# Async session factory cached at module level
_async_session_factory = None


def _get_async_session_factory() -> async_sessionmaker[AsyncSession]:
    """Get or create async session factory."""
    global _async_session_factory
    if _async_session_factory is None:
        from poly_db.database_async import get_async_engine

        engine = get_async_engine()
        _async_session_factory = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _async_session_factory


async def get_async_db() -> AsyncSession:
    """
    Async database session dependency for FastAPI routes.

    Provides an async database session that automatically handles
    commit on success, rollback on exception, and cleanup.

    Usage:
        @router.get("/")
        async def endpoint(session: AsyncSession = Depends(get_async_db)):
            await session.execute(select(User))
    """
    factory = _get_async_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_async_auth_service(db: AsyncSession = Depends(get_async_db)) -> AsyncAuthService:
    """Async version of auth service dependency."""
    settings = get_settings()
    notification_service = get_notification_service()
    return AsyncAuthService(
        db_session=db,
        jwt_secret=settings.JWT_SECRET,
        jwt_expiry_minutes=_parse_expiry_to_minutes(settings.JWT_EXPIRY),
        notification_service=notification_service,
        email_verification_expiry_hours=settings.EMAIL_VERIFICATION_EXPIRY,
        password_reset_expiry_hours=settings.PASSWORD_RESET_EXPIRY,
    )


def get_admin_auth_service(db: Session = Depends(get_db_session)) -> AdminAuthService:
    settings = get_settings()
    return AdminAuthService(
        db_session=db,
        jwt_secret=settings.ADMIN_JWT_SECRET,
        jwt_expiry_minutes=_parse_expiry_to_minutes(settings.JWT_EXPIRY),
    )


async def get_current_user(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db_session),
    auth_service: AuthService = Depends(get_auth_service),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    token = authorization.split(" ", 1)[1].strip()
    payload = auth_service.verify_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    user_id = uuid.UUID(payload["sub"])
    user = UserRepository(db).get_by_id(user_id)
    if not user or not user.is_active or user.is_suspended:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "is_verified": user.is_verified,
        "is_active": user.is_active,
        "is_suspended": user.is_suspended,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }


async def get_current_user_id(current_user: dict = Depends(get_current_user)) -> str:
    return str(current_user["id"])


async def get_current_admin(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db_session),
    admin_auth_service: AdminAuthService = Depends(get_admin_auth_service),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    token = authorization.split(" ", 1)[1].strip()
    payload = admin_auth_service.verify_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

    admin_id = uuid.UUID(payload["sub"])
    admin = AdminUserRepository(db).get_by_id(admin_id)
    if not admin or not admin.is_active or admin.is_suspended:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    return {
        "id": admin.id,
        "email": admin.email,
        "full_name": admin.full_name,
        "role": admin.role,
    }


async def get_current_team_id(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    team_id: str | None = Header(None, alias="X-Team-Id"),
) -> uuid.UUID:
    member_repo = TeamMemberRepository(db)
    if team_id:
        team_uuid = uuid.UUID(team_id)
        member = member_repo.get_by_user_and_team(current_user["id"], team_uuid)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        return team_uuid

    memberships = member_repo.list_by_user_id(current_user["id"])
    if not memberships:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
    return memberships[0].team_id


async def get_team_context(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db_session),
    team_id: str | None = Header(None, alias="X-Team-Id"),
) -> dict:
    """Get full team context including team details."""
    member_repo = TeamMemberRepository(db)

    if team_id:
        team_uuid = uuid.UUID(team_id)
        member = member_repo.get_by_user_and_team(current_user["id"], team_uuid)
        if not member:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        team = db.query(Team).filter(Team.id == team_uuid).first()
    else:
        memberships = member_repo.list_by_user_id(current_user["id"])
        if not memberships:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")
        team = db.query(Team).filter(Team.id == memberships[0].team_id).first()

    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    return {
        "id": team.id,
        "name": team.name,
        "host_language": team.host_language,
        "plan": team.plan.value,
    }
