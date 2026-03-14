"""Qwen3-TTS provider implementation."""

from __future__ import annotations

import asyncio
import io
import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

import numpy as np

from nanobot.voice.base import TTSProvider

if TYPE_CHECKING:
    pass

try:
    import soundfile as sf
    from qwen_tts.inference.qwen3_tts_model import Qwen3TTSModel

    QWEN_TTS_AVAILABLE = True
except ImportError:
    QWEN_TTS_AVAILABLE = False


class QwenTTSProvider(TTSProvider):
    """Qwen3-TTS provider for text-to-speech synthesis."""

    def __init__(
        self,
        model_path: str = "Qwen/Qwen3-TTS-1.7B-Base",
        device: str = "cuda",
        python_path: str = "",
        **kwargs,
    ):
        self.model_path = model_path
        self.device = device
        self.python_path = python_path
        self.kwargs = kwargs
        self._model: Qwen3TTSModel | None = None

        # Check if using subprocess mode
        if not python_path and not QWEN_TTS_AVAILABLE:
            raise ImportError(
                "qwen-tts is not installed. Install with: pip install qwen-tts"
            )

    def _ensure_model(self) -> Qwen3TTSModel:
        """Lazy load model on first use."""
        if self._model is None:
            self._model = Qwen3TTSModel.from_pretrained(
                self.model_path,
                device_map=self.device,
                **self.kwargs,
            )
        return self._model

    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
        language: str = "Auto",
        **kwargs,
    ) -> tuple[bytes, int]:
        """Synthesize speech from text using voice cloning.

        Args:
            text: Text to synthesize
            voice: Voice name (speaker ID for CustomVoice model)
            language: Language code (e.g., "Chinese", "English", "Auto")
            **kwargs: Additional parameters (ref_audio, ref_text, x_vector_only_mode)

        Returns:
            Tuple of (audio_bytes, sample_rate)
        """
        # Use subprocess if python_path is configured
        if self.python_path:
            return await self._synthesize_subprocess(text, language, **kwargs)

        # Direct mode
        model = self._ensure_model()

        # Generate audio
        wavs, sr = model.generate_voice_clone(
            text=text,
            language=language if language != "Auto" else None,
            **kwargs,
        )

        # Convert first audio to bytes
        audio_np = wavs[0]
        buffer = io.BytesIO()
        sf.write(buffer, audio_np, sr, format="WAV")
        audio_bytes = buffer.getvalue()

        return audio_bytes, sr

    async def _synthesize_subprocess(
        self,
        text: str,
        language: str = "Auto",
        **kwargs,
    ) -> tuple[bytes, int]:
        """Synthesize using subprocess in isolated environment."""
        bridge_script = Path(__file__).parent.parent / "bridge.py"

        params = {
            "model_path": self.model_path,
            "device": self.device,
            "text": text,
            "language": language,
        }

        proc = await asyncio.create_subprocess_exec(
            self.python_path,
            str(bridge_script),
            "tts",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate(json.dumps(params).encode())

        if proc.returncode != 0:
            raise RuntimeError(f"TTS subprocess failed: {stderr.decode()}")

        result = json.loads(stdout.decode())
        audio_bytes = bytes.fromhex(result["audio_base64"])
        sample_rate = result["sample_rate"]

        return audio_bytes, sample_rate
