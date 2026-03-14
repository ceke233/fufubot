"""OpenAI DALL-E image generation provider."""

import httpx

from nanobot.image.base import ImageProvider


class OpenAIImageProvider(ImageProvider):
    """OpenAI DALL-E image generation provider."""

    def __init__(self, api_key: str, model: str = "dall-e-3", api_base: str | None = None):
        self.api_key = api_key
        self.model = model
        self.api_base = api_base or "https://api.openai.com/v1"

    async def generate(self, prompt: str, size: str = "1024x1024", **kwargs) -> str:
        """Generate image using DALL-E API."""
        url = f"{self.api_base}/images/generations"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "prompt": prompt,
            "size": size,
            "n": 1,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            return data["data"][0]["url"]
