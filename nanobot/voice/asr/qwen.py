"""Qwen3-ASR provider implementation."""

from __future__ import annotations

import asyncio
import json
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

try:
    from qwen_asr.inference.qwen3_asr import Qwen3ASRModel
    from qwen_asr.inference.utils import normalize_audios

    QWEN_ASR_AVAILABLE = True
except ImportError:
    QWEN_ASR_AVAILABLE = False

from nanobot.voice.base import ASRProvider


class QwenASRProvider(ASRProvider):
    """Qwen3-ASR provider for speech recognition."""

    def __init__(
        self,
        model_path: str = "Qwen/Qwen3-ASR-1.7B",
        device: str = "cuda",
        python_path: str = "",
        **kwargs,
    ):
        self.model_path = model_path
        self.device = device
        self.python_path = python_path
        self.kwargs = kwargs
        self._model: Qwen3ASRModel | None = None

        # Check if using subprocess mode
        if not python_path and not QWEN_ASR_AVAILABLE:
            raise ImportError(
                "qwen-asr is not installed. Install with: pip install qwen-asr"
            )

    def _ensure_model(self) -> Qwen3ASRModel:
        """Lazy load model on first use."""
        if self._model is None:
            self._model = Qwen3ASRModel.from_pretrained(
                self.model_path,
                device_map=self.device,
                **self.kwargs,
            )
        return self._model

    async def transcribe(
        self,
        audio: bytes | str,
        language: str | None = None,
        **kwargs,
    ) -> str:
        """Transcribe speech to text.

        Args:
            audio: Audio data (bytes) or file path (str)
            language: Language code (None for auto-detect)
            **kwargs: Additional parameters (context, return_time_stamps)

        Returns:
            Transcribed text
        """
        # Use subprocess if python_path is configured
        if self.python_path:
            return await self._transcribe_subprocess(audio, language, **kwargs)

        # Direct mode
        model = self._ensure_model()

        # Transcribe audio
        results = model.transcribe(
            audio=audio,
            language=language,
            **kwargs,
        )

        # Return first result text
        return results[0].text if results else ""

    async def _transcribe_subprocess(
        self,
        audio: bytes | str,
        language: str | None = None,
        **kwargs,
    ) -> str:
        """Transcribe using subprocess in isolated environment."""
        bridge_script = Path(__file__).parent.parent / "bridge.py"

        params = {
            "model_path": self.model_path,
            "device": self.device,
            "audio": audio if isinstance(audio, str) else audio.hex(),
            "language": language,
        }

        proc = await asyncio.create_subprocess_exec(
            self.python_path,
            str(bridge_script),
            "asr",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = await proc.communicate(json.dumps(params).encode())

        if proc.returncode != 0:
            raise RuntimeError(f"ASR subprocess failed: {stderr.decode()}")

        result = json.loads(stdout.decode())
        return result["text"]
