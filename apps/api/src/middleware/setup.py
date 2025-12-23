from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from ..config import get_settings

def setup_middleware(app: FastAPI) -> None:
    settings = get_settings()
    
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add other middlewares as needed (e.g., logging, rate limiting)
