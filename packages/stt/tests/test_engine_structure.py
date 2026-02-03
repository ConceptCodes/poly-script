"""Tests for TranslateGemma engine structure (GREEN phase)."""

import ast
from pathlib import Path


def test_translategemma_file_exists():
    """Engine file should exist."""
    engine_path = Path("src/poly_stt/engines/translategemma.py")
    assert engine_path.exists(), f"Engine file not found: {engine_path}"


def test_translategemma_has_translate_method():
    """Engine should have translate method."""
    engine_path = Path("src/poly_stt/engines/translategemma.py")
    tree = ast.parse(engine_path.read_text())

    class_def = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.ClassDef) and n.name == "TranslateGemmaEngine"
    ]
    assert len(class_def) > 0, "TranslateGemmaEngine class not found"

    methods = [n.name for n in ast.walk(class_def[0]) if isinstance(n, ast.FunctionDef)]
    assert "translate" in methods, "translate method not found"
    assert "translate_segments" in methods, "translate_segments method not found"
    assert "_build_translation_prompt" in methods, "_build_translation_prompt method not found"
    assert "_extract_translation" in methods, "_extract_translation method not found"


def test_translategemma_has_correct_imports():
    """Engine should have required imports."""
    engine_path = Path("src/poly_stt/engines/translategemma.py")
    content = engine_path.read_text()

    assert "from transformers import AutoTokenizer, AutoModelForCausalLM" in content
    assert "import torch" in content
    assert "from ..interface import TranscriptionResult, Segment, EngineCapabilities" in content


def test_translategemma_implements_chunking():
    """Engine should implement chunking for large text."""
    engine_path = Path("src/poly_stt/engines/translategemma.py")
    content = engine_path.read_text()

    assert "_should_chunk" in content
    assert "_chunk_text" in content
    assert "_translate_chunked" in content
    assert "MAX_TOKENS = 2048" in content or "MAX_TOKENS=2048" in content


def test_translategemma_has_supported_languages():
    """Engine should list supported languages."""
    engine_path = Path("src/poly_stt/engines/translategemma.py")
    content = engine_path.read_text()

    assert "_get_supported_languages" in content
    assert "en" in content
    assert "es" in content
    assert "fr" in content
    assert "de" in content
    assert "zh" in content
    assert "ja" in content


def test_translategemma_exports_from_engines_init():
    """TranslateGemmaEngine should be exported from engines/__init__.py."""
    init_path = Path("src/poly_stt/engines/__init__.py")
    content = init_path.read_text()

    assert "from .translategemma import TranslateGemmaEngine" in content
    assert "TranslateGemmaEngine" in content
    assert (
        '"WhisperLocalEngine", "TranslateGemmaEngine"' in content
        or "['WhisperLocalEngine', 'TranslateGemmaEngine']" in content
    )
