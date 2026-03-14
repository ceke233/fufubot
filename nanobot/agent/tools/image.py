"""Image generation tool."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from nanobot.image.base import ImageProvider

from nanobot.agent.tools.base import Tool


class ImageGenerationTool(Tool):
    """Generate an image from text description."""

    def __init__(self, provider: ImageProvider, default_size: str = "1024x1024"):
        self.provider = provider
        self.default_size = default_size

    @property
    def name(self) -> str:
        return "generate_image"

    @property
    def description(self) -> str:
        return "Generate an image from a text description"

    @property
    def parameters(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Text description of the image to generate"},
                "size": {"type": "string", "description": "Image size in WIDTHxHEIGHT format (e.g., '1024x1024', '2048x2048'). Supported sizes depend on the provider.", "default": self.default_size},
            },
            "required": ["prompt"],
        }

    async def execute(self, **kwargs) -> str:
        """Execute image generation."""
        prompt = kwargs.get("prompt", "")
        size = kwargs.get("size", self.default_size)

        url = await self.provider.generate(prompt=prompt, size=size)
        return f"Image generated: {url}"
