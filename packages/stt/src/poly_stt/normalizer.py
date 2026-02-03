from .interface import Segment, TranscriptionResult

LANGUAGE_CODE_MAP = {
    "en": "en-US",
    "es": "es-ES",
    "fr": "fr-FR",
    "de": "de-DE",
    "jp": "ja-JP",
    "zh": "zh-CN",
    "it": "it-IT",
    "pt": "pt-BR",
    "ru": "ru-RU",
}


def normalize_language_code(code: str) -> str:
    if not code:
        return "en-US"

    if "-" in code:
        parts = code.split("-")
        if len(parts) >= 2 and len(parts[0]) == 2:
            return code

    code_lower = code.lower()
    if code_lower in LANGUAGE_CODE_MAP:
        return LANGUAGE_CODE_MAP[code_lower]

    return "en-US"


def normalize_segments(segments: list[Segment]) -> list[Segment]:
    if not segments:
        return []

    sorted_segments = sorted(segments, key=lambda s: s.start_ms)

    normalized = []
    last_end = 0
    for seg in sorted_segments:
        if seg.start_ms >= last_end:
            seg.text = seg.text.strip()
            if seg.text:
                normalized.append(seg)
                last_end = seg.end_ms

    return normalized


def validate_result(result: TranscriptionResult) -> None:
    if not result.text:
        raise ValueError("TranscriptionResult.text cannot be empty")

    if not result.language:
        raise ValueError("TranscriptionResult.language is required")

    if not result.engine:
        raise ValueError("TranscriptionResult.engine is required")

    for i, seg in enumerate(result.segments):
        if seg.start_ms < 0:
            raise ValueError(f"Segment {i}: start_ms cannot be negative")

        if seg.end_ms < seg.start_ms:
            raise ValueError(f"Segment {i}: end_ms must be >= start_ms")

        if not seg.text:
            raise ValueError(f"Segment {i}: text cannot be empty")

    if result.confidence is not None and not (0.0 <= result.confidence <= 1.0):
        raise ValueError("confidence must be between 0.0 and 1.0")


def normalize_result(result: TranscriptionResult) -> TranscriptionResult:
    result.language = normalize_language_code(result.language)
    result.segments = normalize_segments(result.segments)
    validate_result(result)
    return result
