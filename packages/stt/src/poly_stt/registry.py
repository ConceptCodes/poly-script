from typing import List, Optional
from .interface import STTEngine, EngineCapabilities

class EngineRegistry:
    _engines: dict[str, STTEngine] = {}
    _default: Optional[str] = None
    
    @classmethod
    def register(cls, engine: STTEngine) -> None:
        cls._engines[engine.name] = engine
    
    @classmethod
    def get(cls, name: Optional[str] = None) -> STTEngine:
        if name is None:
            name = cls._default
        
        if name not in cls._engines:
            raise ValueError(f"Unknown engine: {name}")
        
        return cls._engines[name]
    
    @classmethod
    def list_engines(cls) -> List[dict[str, object]]:
        return [
            {
                "name": engine.name,
                "capabilities": engine.capabilities,
            }
            for engine in cls._engines.values()
        ]
    
    @classmethod
    def set_default(cls, name: str) -> None:
        if name not in cls._engines:
            raise ValueError(f"Cannot set default: unknown engine {name}")
        cls._default = name
    
    @classmethod
    def is_default_set(cls) -> bool:
        return cls._default is not None