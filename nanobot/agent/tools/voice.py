"""Voice tools for TTS and ASR."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nanobot.voice.base import ASRProvider, TTSProvider

from nanobot.agent.tools.base import Tool


class TextToSpeechTool(Tool):
    """Convert text to speech and save as audio file."""

    def __init__(self, provider: TTSProvider):
        self.provider = provider

    @property
    def name(self) -> str:
        return "text_to_speech"

    @property
    def description(self) -> str:
        return "Convert text to speech and save as audio file"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Text to synthesize"},
                "output_path": {"type": "string", "description": "Output audio file path"},
                "voice": {"type": "string", "description": "Voice name (optional)"},
                "language": {"type": "string", "description": "Language (e.g., Chinese, English, Auto)"},
            },
            "required": ["text", "output_path"],
        }

    async def execute(self, **kwargs) -> str:
        """Execute TTS synthesis."""
        text = kwargs.get("text", "")
        output_path = kwargs.get("output_path", "")
        voice = kwargs.get("voice")
        language = kwargs.get("language", "Auto")

        # Synthesize audio
        audio_bytes, sr = await self.provider.synthesize(
            text=text,
            voice=voice,
            language=language,
        )

        # Save to file
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(audio_bytes)

        return f"Speech saved to {output_path} (sample_rate={sr}Hz)"


class SpeechToTextTool(Tool):
    """Convert speech audio file to text."""

    def __init__(self, provider: ASRProvider):
        self.provider = provider

    @property
    def name(self) -> str:
        return "speech_to_text"

    @property
    def description(self) -> str:
        return "Convert speech audio file to text"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "audio_path": {"type": "string", "description": "Audio file path"},
                "language": {"type": "string", "description": "Language (optional, e.g., Chinese)"},
            },
            "required": ["audio_path"],
        }

    async def execute(self, **kwargs) -> str:
        """Execute ASR transcription."""
        audio_path = kwargs.get("audio_path", "")
        language = kwargs.get("language")

        # Transcribe audio
        text = await self.provider.transcribe(
            audio=audio_path,
            language=language,
        )

        return f"Transcription: {text}"

