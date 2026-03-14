"""Voice provider registry."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class VoiceProviderSpec:
    """Voice provider specification."""

    name: str  # Config field name (e.g., "qwen_tts")
    provider_type: str  # "tts" or "asr"
    display_name: str  # Display name
    default_model: str  # Default model
    requires_api_key: bool  # Whether API key is required


TTS_PROVIDERS: tuple[VoiceProviderSpec, ...] = (
    VoiceProviderSpec(
        name="qwen_tts",
        provider_type="tts",
        display_name="Qwen3-TTS",
        default_model="Qwen/Qwen3-TTS-1.7B-Base",
        requires_api_key=False,
    ),
)

ASR_PROVIDERS: tuple[VoiceProviderSpec, ...] = (
    VoiceProviderSpec(
        name="qwen_asr",
        provider_type="asr",
        display_name="Qwen3-ASR",
        default_model="Qwen/Qwen3-ASR-1.7B",
        requires_api_key=False,
    ),
)
