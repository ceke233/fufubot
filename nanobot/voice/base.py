"""Voice providers base classes."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """Text-to-Speech provider base class."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
        language: str = "Auto",
        **kwargs,
    ) -> tuple[bytes, int]:
        """Synthesize speech from text.

        Args:
            text: Text to synthesize
            voice: Voice name/ID (provider-specific)
            language: Language code (e.g., "Chinese", "English", "Auto")
            **kwargs: Provider-specific parameters

        Returns:
            Tuple of (audio_data, sample_rate)
        """


class ASRProvider(ABC):
    """Automatic Speech Recognition provider base class."""

    @abstractmethod
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
            **kwargs: Provider-specific parameters

        Returns:
            Transcribed text
        """
