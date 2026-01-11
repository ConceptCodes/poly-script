from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from poly_core.constants import I18nKeys
from poly_core.services.i18n import I18nService
from src.middleware.setup import setup_middleware

# Direct imports from route modules (avoid src package issues)
from src.routes.auth import auth_router
from src.routes.billing import billing_router
from src.routes.health import health_router
from src.routes.jobs import jobs_router
from src.routes.onboarding import onboarding_router
from src.routes.teams import teams_router
from src.routes.webhooks import webhooks_router
from src.routes.transcripts import transcripts_router

# Import worker service
from src.worker.service import WorkerService

# Global worker service instance
worker_service = WorkerService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    print("🚀 Starting PolyScript API...")

    # Start worker thread
    worker_service.start()
    print("✅ Worker started")

    yield

    # Shutdown
    print("🛑 Shutting down PolyScript API...")

    # Stop worker thread
    worker_service.stop()
    print("✅ Worker stopped")


def create_app() -> FastAPI:
    app = FastAPI(
        title="PolyScript API",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Initialize i18n service
    # locales dir is relative to this file: ./src/locales
    current_dir = Path(__file__).parent
    locales_dir = current_dir / "src" / "locales"
    global i18n_service
    i18n_service = I18nService(locales_dir)

    setup_middleware(app)

    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(teams_router)
    app.include_router(onboarding_router)
    app.include_router(billing_router)
    app.include_router(webhooks_router)
    app.include_router(jobs_router)
    app.include_router(transcripts_router)

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
            "worker": "active" if worker_service.is_running else "inactive",
        }

    return app


app = create_app()
