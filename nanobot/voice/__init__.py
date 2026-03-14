"""Voice module for TTS and ASR."""

from __future__ import annotations

from nanobot.voice.base import ASRProvider, TTSProvider
from nanobot.voice.registry import ASR_PROVIDERS, TTS_PROVIDERS, VoiceProviderSpec

__all__ = [
    "TTSProvider",
    "ASRProvider",
    "VoiceProviderSpec",
    "TTS_PROVIDERS",
    "ASR_PROVIDERS",
]
