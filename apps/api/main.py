
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI

from poly_core.constants import I18nKeys
from poly_core.services.i18n import I18nService
from src.middleware.setup import setup_middleware
from src.logging import setup_logging

# Direct imports from route modules (avoid src package issues)
from src.routes.auth import auth_router
from src.routes.billing import billing_router
from src.routes.health import health_router
from src.routes.jobs import jobs_router
from src.routes.onboarding import onboarding_router
from src.routes.teams import teams_router
from src.routes.webhooks import webhooks_router
from src.routes.transcripts import transcripts_router
from src.routes.engines import router as engines_router
from src.routes.admin import router as admin_router
from src.routes.contact import router as contact_router
from src.routes.dashboard import router as dashboard_router
from src.routes.settings import router as settings_router
from src.routes.user import router as user_router

from poly_stt.bootstrap import initialize_engines

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown."""
    # Startup
    print("🚀 Starting PolyScript API Lifespan...")

    # Initialize STT engines (needed for engine capabilities endpoint)
    # initialize_engines()

    # Note: Worker service runs as a separate process (apps/worker)
    # Start it independently with: cd apps/worker && python main.py

    print("✅ PolyScript API Lifespan ready.")
    yield

    # Shutdown
    print("🛑 Shutting down PolyScript API...")


def create_app() -> FastAPI:
    print("🛠️ Entering create_app()...")
    setup_logging()
    app = FastAPI(
        title="PolyScript API",
        version="0.1.0",
        lifespan=lifespan,
    )
    print("✅ FastAPI app created.")

    # Initialize i18n service
    # locales dir is relative to this file: ./src/locales
    current_dir = Path(__file__).parent
    locales_dir = current_dir / "src" / "locales"
    global i18n_service
    print(f"🌍 Initializing I18nService with {locales_dir}...")
    i18n_service = I18nService(locales_dir)
    print("✅ I18nService initialized.")

    print("🛡️ Setting up middleware...")
    setup_middleware(app)
    print("✅ Middleware setup.")

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
    print("✅ Routes included.")

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
