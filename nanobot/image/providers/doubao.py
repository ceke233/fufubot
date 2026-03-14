"""Doubao Seedream image generation provider."""

import os

from openai import OpenAI

from nanobot.image.base import ImageProvider


class DoubaoSeedreamProvider(ImageProvider):
    """Doubao Seedream image generation provider."""

    def __init__(
        self,
        api_key: str = "",
        model: str = "doubao-seedream-4-5-251128",
        base_url: str = "https://ark.cn-beijing.volces.com/api/v3",
    ):
        self.api_key = api_key or os.environ.get("ARK_API_KEY", "")
        self.model = model
        self.base_url = base_url
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key)

    async def generate(self, prompt: str, size: str = "1024x1024", **kwargs) -> str:
        """Generate image using Doubao Seedream API.

        Note: The 'size' parameter is ignored as Doubao API does not support custom sizes.

        Supported sizes (aspect ratios):
        - 1:1  → 2048x2048
        - 4:3  → 2304x1728
        - 3:4  → 1728x2304
        - 16:9 → 2848x1600
        - 9:16 → 1600x2848
        - 3:2  → 2496x1664
        - 2:3  → 1664x2496
        """
        response = self.client.images.generate(
            model=self.model,
            prompt=prompt,
            response_format="url",
            extra_body={"watermark": kwargs.get("watermark", False)},
        )

        if response.data and response.data[0].url:
            return response.data[0].url
        return ""
