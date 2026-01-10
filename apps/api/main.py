from pathlib import Path

from fastapi import Depends, FastAPI

from poly_core.constants import I18nKeys
from poly_core.services.i18n import I18nService
from src.dependencies import get_locale
from src.middleware.setup import setup_middleware
from src.routes import auth, billing, health, onboarding, teams, webhooks


def create_app() -> FastAPI:
    app = FastAPI(title="PolyScript API", version="0.1.0")

    # Initialize i18n service
    # locales dir is relative to this file: ./src/locales
    current_dir = Path(__file__).parent
    locales_dir = current_dir / "src" / "locales"
    global i18n_service
    i18n_service = I18nService(locales_dir)

    setup_middleware(app)

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(teams.router)
    app.include_router(onboarding.router)
    app.include_router(billing.router)
    app.include_router(webhooks.router)

    @app.get("/v1/debug/i18n")
    async def debug_i18n(locale: str = Depends(get_locale)):
        """Temporary endpoint to verify i18n parsing"""
        return {
            "detected_locale": locale,
            "greeting": i18n_service.t(
                I18nKeys.NOTIFICATION_INVITATION_SUBJECT, locale=locale, team_name="Acme"
            ),
        }

    return app


app = create_app()
