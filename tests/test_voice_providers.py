"""Tests for voice providers (TTS/ASR)."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

pytestmark = pytest.mark.asyncio

# Integration test configuration
VOICE_ENV_PYTHON = os.getenv(
    "VOICE_ENV_PYTHON", "/home/ceke233/miniconda3/envs/qwen3-asr-tts/bin/python"
)
SKIP_INTEGRATION = not Path(VOICE_ENV_PYTHON).exists()


class TestQwenTTSProvider:
    """Test Qwen TTS provider."""

    async def test_init_without_dependencies(self):
        """Test initialization fails without qwen-tts installed."""
        from nanobot.voice.tts.qwen import QWEN_TTS_AVAILABLE, QwenTTSProvider

        if not QWEN_TTS_AVAILABLE:
            with pytest.raises(ImportError, match="qwen-tts is not installed"):
                QwenTTSProvider(python_path="")

    async def test_init_with_subprocess_mode(self):
        """Test initialization with subprocess mode."""
        from nanobot.voice.tts.qwen import QwenTTSProvider

        provider = QwenTTSProvider(python_path="/usr/bin/python3")
        assert provider.python_path == "/usr/bin/python3"
        assert provider.model_path == "Qwen/Qwen3-TTS-1.7B-Base"

    @pytest.mark.integration
    @pytest.mark.skipif(SKIP_INTEGRATION, reason="Voice environment not available")
    async def test_synthesize_integration(self, tmp_path):
        """Integration test: synthesize speech from text."""
        from nanobot.voice.tts.qwen import QwenTTSProvider

        provider = QwenTTSProvider(python_path=VOICE_ENV_PYTHON, device="cpu")

        # Synthesize short text
        audio_bytes, sample_rate = await provider.synthesize(
            text="你好世界", language="Chinese"
        )

        # Verify output
        assert isinstance(audio_bytes, bytes)
        assert len(audio_bytes) > 0
        assert sample_rate > 0

        # Save to file for manual verification
        output_file = tmp_path / "test_tts.wav"
        output_file.write_bytes(audio_bytes)
        assert output_file.exists()


class TestQwenASRProvider:
    """Test Qwen ASR provider."""

    async def test_init_without_dependencies(self):
        """Test initialization fails without qwen-asr installed."""
        from nanobot.voice.asr.qwen import QWEN_ASR_AVAILABLE, QwenASRProvider

        if not QWEN_ASR_AVAILABLE:
            with pytest.raises(ImportError, match="qwen-asr is not installed"):
                QwenASRProvider(python_path="")

    async def test_init_with_subprocess_mode(self):
        """Test initialization with subprocess mode."""
        from nanobot.voice.asr.qwen import QwenASRProvider

        provider = QwenASRProvider(python_path="/usr/bin/python3")
        assert provider.python_path == "/usr/bin/python3"
        assert provider.model_path == "Qwen/Qwen3-ASR-1.7B"

    @pytest.mark.integration
    @pytest.mark.skipif(SKIP_INTEGRATION, reason="Voice environment not available")
    async def test_transcribe_integration(self, tmp_path):
        """Integration test: transcribe speech to text."""
        from nanobot.voice.asr.qwen import QwenASRProvider
        from nanobot.voice.tts.qwen import QwenTTSProvider

        # First generate test audio using TTS
        tts_provider = QwenTTSProvider(python_path=VOICE_ENV_PYTHON, device="cpu")
        test_text = "今天天气真好"
        audio_bytes, _ = await tts_provider.synthesize(
            text=test_text, language="Chinese"
        )

        # Save audio to file
        audio_file = tmp_path / "test_audio.wav"
        audio_file.write_bytes(audio_bytes)

        # Transcribe the audio
        asr_provider = QwenASRProvider(python_path=VOICE_ENV_PYTHON, device="cpu")
        transcribed_text = await asr_provider.transcribe(
            audio=str(audio_file), language="Chinese"
        )

        # Verify output
        assert isinstance(transcribed_text, str)
        assert len(transcribed_text) > 0
        # Note: exact match may not be guaranteed due to model limitations
        print(f"Original: {test_text}")
        print(f"Transcribed: {transcribed_text}")
