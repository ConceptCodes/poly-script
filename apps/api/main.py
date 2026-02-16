import logging
import uuid
from contextlib import asynccontextmanager
from pathlib import Path
from threading import Thread

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from poly_core.constants import I18nKeys
from poly_core.services.i18n import I18nService
from src.structured_logging import StructuredLogger, setup_logging
from src.middleware.setup import setup_middleware
from src.routes.admin import router as admin_router

# Direct imports from route modules (avoid src package issues)
from src.routes.auth import auth_router
from src.routes.billing import billing_router
from src.routes.contact import router as contact_router
from src.routes.dashboard import router as dashboard_router
from src.routes.engines import router as engines_router
from src.routes.health import health_router
from src.routes.jobs import jobs_router
from src.routes.onboarding import onboarding_router
from src.routes.settings import router as settings_router
from src.routes.teams import teams_router
from src.routes.transcripts import transcripts_router
from src.routes.user import router as user_router
from src.routes.webhooks import webhooks_router
from poly_core.logging_context import set_request_context

# Import standardized exception handlers
from poly_core.exceptions.handlers import setup_exception_handlers
from poly_core.exceptions.base import ErrorResponse

logger = logging.getLogger(__name__)

# Global scheduler for cron jobs
scheduler: AsyncIOScheduler | None = None


async def add_request_id(request: Request, call_next):
    """Middleware to inject request_id into structured logging context."""
    request_id = str(uuid.uuid4())
    set_request_context(request_id)

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


def setup_cron_jobs(scheduler: AsyncIOScheduler) -> None:
    """Configure scheduled jobs for maintenance tasks."""
    from poly_core.tasks.billing_tasks import reset_all_monthly_usage, sync_active_subscriptions
    from poly_core.tasks.cleanup_tasks import (
        cleanup_audio_files,
        cleanup_expired_invitations,
        cleanup_expired_password_resets,
        cleanup_orphaned_content,
        cleanup_revoked_tokens,
        hard_delete_soft_deleted_content,
    )

    # Hourly tasks
    scheduler.add_job(
        cleanup_expired_password_resets,
        "cron",
        minute=0,
        id="cleanup_expired_password_resets",
        name="Clean up expired password resets",
    )

    scheduler.add_job(
        reset_all_monthly_usage,
        "cron",
        minute=5,
        id="reset_monthly_usage",
        name="Reset monthly usage counters",
    )

    # Daily tasks (run at 2 AM)
    scheduler.add_job(
        cleanup_expired_invitations,
        "cron",
        hour=2,
        minute=0,
        id="cleanup_expired_invitations",
        name="Clean up expired invitations",
    )

    scheduler.add_job(
        cleanup_revoked_tokens,
        "cron",
        hour=3,
        minute=0,
        id="cleanup_revoked_tokens",
        name="Clean up revoked refresh tokens",
    )

    scheduler.add_job(
        hard_delete_soft_deleted_content,
        "cron",
        hour=4,
        minute=0,
        id="hard_delete_soft_deleted_content",
        name="Hard delete soft-deleted content",
    )

    scheduler.add_job(
        cleanup_orphaned_content,
        "cron",
        hour=5,
        minute=0,
        id="cleanup_orphaned_content",
        name="Clean up orphaned content",
    )

    scheduler.add_job(
        cleanup_audio_files,
        "cron",
        hour=6,
        minute=0,
        id="cleanup_audio_files",
        name="Clean up orphaned audio files",
    )

    scheduler.add_job(
        sync_active_subscriptions,
        "cron",
        hour=1,
        minute=30,
        id="sync_stripe_subscriptions",
        name="Sync Stripe subscriptions",
    )


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    global scheduler

    setup_logging()
    logger.info("Starting PolyScript API Lifespan...")

    # Start cron scheduler
    scheduler = AsyncIOScheduler()
    setup_cron_jobs(scheduler)
    scheduler.start()
    logger.info("Cron scheduler started")

    logger.info("PolyScript API Lifespan ready.")
    yield

    logger.info("Shutting down PolyScript API...")

    # Shutdown scheduler gracefully
    if scheduler:
        scheduler.shutdown(wait=False)
        logger.info("Cron scheduler stopped")

    logger.info("PolyScript API shutdown complete.")


def create_app() -> FastAPI:
    setup_logging()
    logger.info("Entering create_app()...")

    app = FastAPI(
        title="PolyScript API",
        version="0.1.0",
        lifespan=lifespan,
        responses={
            400: {"description": "Bad Request", "model": ErrorResponse},
            401: {"description": "Unauthorized", "model": ErrorResponse},
            403: {"description": "Forbidden", "model": ErrorResponse},
            404: {"description": "Not Found", "model": ErrorResponse},
            409: {"description": "Conflict", "model": ErrorResponse},
            422: {"description": "Validation Error", "model": ErrorResponse},
            429: {"description": "Rate Limit Exceeded", "model": ErrorResponse},
            500: {"description": "Internal Server Error", "model": ErrorResponse},
        },
    )
    logger.info("FastAPI app created.")

    # Request ID middleware
    app.middleware("http")(add_request_id)

    # Initialize i18n service
    # locales dir is relative to this file: ./src/locales
    current_dir = Path(__file__).parent
    locales_dir = current_dir / "src" / "locales"
    global i18n_service
    logger.info(f"Initializing I18nService with {locales_dir}...")
    i18n_service = I18nService(locales_dir)
    logger.info("I18nService initialized.")

    # Setup global exception handlers with i18n support
    logger.info("Setting up global exception handlers...")
    setup_exception_handlers(app, i18n_service)
    logger.info("Global exception handlers registered.")

    logger.info("Setting up middleware...")
    setup_middleware(app)
    logger.info("Middleware setup.")

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(teams_router)
    app.include_router(onboarding_router)
    app.include_router(billing_router)
    app.include_router(webhooks_router)
    app.include_router(jobs_router)
    app.include_router(transcripts_router)
    app.include_router(engines_router)
    app.include_router(admin_router)
    app.include_router(contact_router)
    app.include_router(dashboard_router)
    app.include_router(settings_router)
    app.include_router(user_router)
    logger.info("Routes included.")

    @app.get("/v1/debug/i18n")
    async def debug_i18n(locale: str):
        """Temporary endpoint to verify i18n parsing"""
        return {
            "detected_locale": locale,
            "greeting": i18n_service.t(
                I18nKeys.NOTIFICATION_INVITATION_SUBJECT, locale=locale, team_name="Acme"
            ),
        }

    @app.get("/")
    async def root():
        return {
            "name": "PolyScript API",
            "version": "0.1.0",
            "status": "running",
        }

    return app


app = create_app()
