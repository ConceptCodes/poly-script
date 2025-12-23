from fastapi import FastAPI
from src.routes import health
from src.config import get_settings
from src.middleware.setup import setup_middleware

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="PolyScript API", version="0.1.0")

    setup_middleware(app)

    app.include_router(health.router)

    return app

app = create_app()
