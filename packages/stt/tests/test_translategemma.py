"""Tests for TranslateGemma translation engine (TDD with mocks)."""

from unittest.mock import MagicMock, patch

from poly_stt.engines.translategemma import TranslateGemmaEngine
from poly_stt.interface import EngineCapabilities, Segment, TranscriptionResult


class TestTranslateGemmaEngine:
    """Tests for TranslateGemma engine functionality (mocked)."""

    def test_engine_exists(self):
        """Engine class should be importable."""
        assert TranslateGemmaEngine is not None

    @patch("poly_stt.engines.translategemma.AutoTokenizer")
    @patch("poly_stt.engines.translategemma.AutoModelForCausalLM")
    def test_engine_has_name(self, _mock_model, _mock_tokenizer):
        """Engine should have a name property."""
        engine = TranslateGemmaEngine()
        assert engine.name is not None
        assert "translategemma" in engine.name.lower()

    @patch("poly_stt.engines.translategemma.AutoTokenizer")
    @patch("poly_stt.engines.translategemma.AutoModelForCausalLM")
    def test_engine_has_capabilities(self, _mock_model, _mock_tokenizer):
        """Engine should report capabilities."""
        engine = TranslateGemmaEngine()
        assert isinstance(engine.capabilities, EngineCapabilities)

    @patch("poly_stt.engines.translategemma.AutoTokenizer")
    @patch("poly_stt.engines.translategemma.AutoModelForCausalLM")
    def test_translate_with_segments(self, mock_model, mock_tokenizer):
        """Engine should translate text with segment timing preserved."""
        # Mock the tokenizer and model
        mock_tok = MagicMock()
        mock_tok.return_value.input_ids = [1, 2, 3, 4, 5]
        mock_tokenizer.from_pretrained.return_value = mock_tok
        mock_tok.apply_chat_template.return_value = "Translate to Spanish: Hello world"

        mock_model_instance = MagicMock()
        mock_model_instance.generate.return_value = [[1, 2, 3, 4, 5, 6, 7, 8]]
        mock_model.from_pretrained.return_value = mock_model_instance
        mock_tok.decode.return_value = "model> Hola mundo"

        engine = TranslateGemmaEngine()

        segments = [
            Segment(start_ms=0, end_ms=1000, text="Hello"),
            Segment(start_ms=1000, end_ms=2000, text="How are you?"),
        ]

        result = engine.translate_segments(
            segments=segments, target_language="es", source_language="en"
        )

        assert len(result.segments) == 2
        assert result.segments[0].start_ms == 0
        assert result.segments[0].end_ms == 1000
        assert result.segments[1].start_ms == 1000
        assert result.segments[1].end_ms == 2000
        assert result.language == "es"

    @patch("poly_stt.engines.translategemma.AutoTokenizer")
    @patch("poly_stt.engines.translategemma.AutoModelForCausalLM")
    def test_normalize_translation_output(self, mock_model, mock_tokenizer):
        """Translation output should match TranscriptionResult shape."""
        # Mock the model
        mock_tok = MagicMock()
        mock_tok.return_value.input_ids = [1, 2, 3]
        mock_tokenizer.from_pretrained.return_value = mock_tok
        mock_tok.apply_chat_template.return_value = "Translate: Hello"
        mock_model_instance = MagicMock()
        mock_model_instance.generate.return_value = [[1, 2, 3, 4]]
        mock_model.from_pretrained.return_value = mock_model_instance
        mock_tok.decode.return_value = "model> Hola"

        engine = TranslateGemmaEngine()

        result = engine.translate(text="Hello", target_language="es", source_language="en")

        assert isinstance(result, TranscriptionResult)
        assert hasattr(result, "text")
        assert hasattr(result, "language")
        assert hasattr(result, "segments")
        assert hasattr(result, "engine")

    @patch("poly_stt.engines.translategemma.AutoTokenizer")
    @patch("poly_stt.engines.translategemma.AutoModelForCausalLM")
    def test_chunking_large_text(self, mock_model, mock_tokenizer):
        """Engine should handle large text by chunking (2k token limit)."""
        # Mock tokenizer to return large token count
        mock_tok = MagicMock()

        def mock_tokenize(text):
            mock_result = MagicMock()
            # Simulate 1 token per 2 characters
            token_count = len(text) // 2
            mock_result.__getitem__ = (
                lambda _self, key: [1] * token_count if key == "input_ids" else token_count
            )
            return mock_result

        mock_tok.return_value = mock_tokenize(None)
        mock_tokenizer.from_pretrained.return_value = mock_tok
        mock_tok.apply_chat_template.return_value = "Translate: {text}"
        mock_tok.decode.return_value = "model> Translated text"

        mock_model_instance = MagicMock()
        mock_model_instance.generate.return_value = [[1, 2, 3]]
        mock_model.from_pretrained.return_value = mock_model_instance

        engine = TranslateGemmaEngine()

        # Generate text longer than 2k tokens
        long_text = "This is a sentence. " * 200  # Should trigger chunking

        result = engine.translate(text=long_text, target_language="es", source_language="en")

        assert result is not None
        assert result.text != ""
        assert result.language == "es"

    @patch("poly_stt.engines.translategemma.AutoTokenizer")
    @patch("poly_stt.engines.translategemma.AutoModelForCausalLM")
    def test_supported_languages(self, mock_model, mock_tokenizer):
        """Engine should return list of supported languages."""
        mock_model_instance = MagicMock()
        mock_model.from_pretrained.return_value = mock_model_instance
        mock_tok = MagicMock()
        mock_tokenizer.from_pretrained.return_value = mock_tok

        engine = TranslateGemmaEngine()

        languages = engine.capabilities.supported_languages
        assert languages is not None
        assert isinstance(languages, list)
        assert len(languages) > 0
        assert "en" in languages
        assert "es" in languages
        assert "fr" in languages
        assert "de" in languages
