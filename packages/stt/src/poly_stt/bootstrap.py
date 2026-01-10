from .engines import WhisperLocalEngine
from .registry import EngineRegistry
import os

def initialize_engines():
    model_size = os.getenv("WHISPER_MODEL_SIZE", "base")
    
    valid_sizes = ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"]
    if model_size not in valid_sizes:
        raise ValueError(
            f"Invalid WHISPER_MODEL_SIZE: {model_size}. "
            f"Valid options: {', '.join(valid_sizes)}"
        )
    
    whisper_engine = WhisperLocalEngine(model_size=model_size)
    EngineRegistry.register(whisper_engine)
    EngineRegistry.set_default(whisper_engine.name)
    
    print(f"[STT] Registered engine: {whisper_engine.name}")
    print(f"[STT] Set default engine: {EngineRegistry._default}")