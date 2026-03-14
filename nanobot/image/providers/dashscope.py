"""DashScope (通义万相) image generation provider."""

import asyncio

import httpx

from nanobot.image.base import ImageProvider


class DashScopeImageProvider(ImageProvider):
    """DashScope Text2Image provider."""

    def __init__(self, api_key: str, model: str = "wanx-v1"):
        self.api_key = api_key
        self.model = model
        self.api_base = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text2image/image-synthesis"

    async def generate(self, prompt: str, size: str = "1024x1024", **kwargs) -> str:
        """Generate image using DashScope API (async task mode)."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-DashScope-Async": "enable",
        }
        payload = {
            "model": self.model,
            "input": {"prompt": prompt},
            "parameters": {"size": size},
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            # Submit task
            resp = await client.post(self.api_base, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            task_id = data["output"]["task_id"]

            # Poll for result
            status_url = f"https://dashscope.aliyuncs.com/api/v1/tasks/{task_id}"
            for _ in range(60):  # Max 60 attempts (5 minutes)
                await asyncio.sleep(5)
                status_resp = await client.get(status_url, headers=headers)
                status_resp.raise_for_status()
                status_data = status_resp.json()

                task_status = status_data["output"]["task_status"]
                if task_status == "SUCCEEDED":
                    return status_data["output"]["results"][0]["url"]
                elif task_status == "FAILED":
                    raise RuntimeError(f"Image generation failed: {status_data}")

            raise TimeoutError("Image generation timed out")
