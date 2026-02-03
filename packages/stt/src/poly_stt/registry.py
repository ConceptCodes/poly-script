from typing import ClassVar

from poly_stt.interface import STTEngine


class EngineRegistry:
    _engines: ClassVar[dict[str, STTEngine]] = {}
    _default: ClassVar[str | None] = None

    @classmethod
    def register(cls, engine: STTEngine) -> None:
        cls._engines[engine.name] = engine

    @classmethod
    def get(cls, name: str | None = None) -> STTEngine:
        if name is None:
            name = cls._default

        if name not in cls._engines:
            raise ValueError(f"Unknown engine: {name}")

        return cls._engines[name]

    @classmethod
    def list_engines(cls) -> list[dict[str, object]]:
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
