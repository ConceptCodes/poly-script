from fastapi import FastAPI, Depends, Request
from src.routes import health, billing, webhooks
from src.config import get_settings
from src.middleware.setup import setup_middleware
from src.dependencies import get_locale
from poly_core.services.i18n import I18nService
from poly_core.constants import I18nKeys
import os

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="PolyScript API", version="0.1.0")

    # Initialize i18n service
    # locales dir is relative to this file: ./src/locales
    current_dir = os.path.dirname(os.path.abspath(__file__))
    locales_dir = os.path.join(current_dir, "src", "locales")
    global i18n_service
    i18n_service = I18nService(locales_dir)

    setup_middleware(app)

    app.include_router(health.router)
    app.include_router(billing.router)
    app.include_router(webhooks.router)

    @app.get("/v1/debug/i18n")
    async def debug_i18n(locale: str = Depends(get_locale)):
        """Temporary endpoint to verify i18n parsing"""
        return {
            "detected_locale": locale,
            "greeting": i18n_service.t(I18nKeys.NOTIF_INVITATION_SUBJECT, locale=locale, team_name="Acme")
        }

    return app

app = create_app()
