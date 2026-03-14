"""Integration tests for image generation (requires real API keys)."""

import os

import pytest


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="Requires OPENAI_API_KEY environment variable",
)
@pytest.mark.asyncio
async def test_openai_image_generation_real():
    """Test real OpenAI DALL-E image generation."""
    from nanobot.image.providers.openai import OpenAIImageProvider

    provider = OpenAIImageProvider(
        api_key=os.getenv("OPENAI_API_KEY"),
        model="dall-e-3",
    )

    url = await provider.generate(
        prompt="A cute cat sitting on a laptop",
        size="1024x1024",
    )

    assert url.startswith("http")
    assert "blob.core.windows.net" in url or "oaidalleapiprodscus" in url
    print(f"Generated image URL: {url}")


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("DASHSCOPE_API_KEY"),
    reason="Requires DASHSCOPE_API_KEY environment variable",
)
@pytest.mark.asyncio
async def test_dashscope_image_generation_real():
    """Test real DashScope image generation."""
    from nanobot.image.providers.dashscope import DashScopeImageProvider

    provider = DashScopeImageProvider(
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        model="wanx-v1",
    )

    url = await provider.generate(
        prompt="一只可爱的猫咪坐在笔记本电脑上",
        size="1024x1024",
    )

    assert url.startswith("http")
    print(f"Generated image URL: {url}")


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ARK_API_KEY"),
    reason="Requires ARK_API_KEY environment variable",
)
@pytest.mark.asyncio
async def test_doubao_image_generation_real():
    """Test real Doubao Seedream image generation."""
    from nanobot.image.providers.doubao import DoubaoSeedreamProvider

    provider = DoubaoSeedreamProvider(
        api_key=os.getenv("ARK_API_KEY"),
        model="doubao-seedream-4-5-251128",
    )

    url = await provider.generate(
        prompt="一只可爱的猫咪坐在笔记本电脑上，赛博朋克风格",
        size="1024x1024",
    )

    assert url.startswith("http")
    print(f"Generated image URL: {url}")
