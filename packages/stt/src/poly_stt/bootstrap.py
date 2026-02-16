import logging
import os

from .engines import WhisperLocalEngine
from .registry import EngineRegistry

logger = logging.getLogger(__name__)


def initialize_engines():
    """Initialize and register STT engines."""
    model_size = os.getenv("WHISPER_MODEL_SIZE", "medium")

    valid_sizes = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
    if model_size not in valid_sizes:
        raise ValueError(
            f"Invalid WHISPER_MODEL_SIZE: {model_size}. Valid options: {', '.join(valid_sizes)}"
        )

    whisper_engine = WhisperLocalEngine(model_size=model_size)
    EngineRegistry.register(whisper_engine)
    EngineRegistry.set_default(whisper_engine.name)

    logger.info("Registered engine: %s", whisper_engine.name)
    logger.info("Set default engine: %s", EngineRegistry._default)
