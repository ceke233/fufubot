"""Test image generation functionality."""

import pytest

from nanobot.config.schema import Config, ImageConfig


def test_image_config_default():
    """Test default ImageConfig."""
    config = ImageConfig()
    assert config.enabled is False
    assert config.provider == "openai"
    assert config.model == ""
    assert config.api_key == ""
    assert config.default_size == "1024x1024"


def test_image_config_in_root_config():
    """Test ImageConfig is accessible from root Config."""
    config = Config()
    assert hasattr(config, "image")
    assert isinstance(config.image, ImageConfig)


def test_image_config_enabled():
    """Test ImageConfig with enabled=True."""
    config = ImageConfig(
        enabled=True,
        provider="openai",
        model="dall-e-3",
        api_key="test-key",
    )
    assert config.enabled is True
    assert config.provider == "openai"
    assert config.model == "dall-e-3"
    assert config.api_key == "test-key"


@pytest.mark.asyncio
async def test_openai_provider_interface():
    """Test OpenAI provider has correct interface."""
    from nanobot.image.providers.openai import OpenAIImageProvider

    provider = OpenAIImageProvider(api_key="test-key", model="dall-e-3")
    assert hasattr(provider, "generate")
    assert callable(provider.generate)


@pytest.mark.asyncio
async def test_dashscope_provider_interface():
    """Test DashScope provider has correct interface."""
    from nanobot.image.providers.dashscope import DashScopeImageProvider

    provider = DashScopeImageProvider(api_key="test-key", model="wanx-v1")
    assert hasattr(provider, "generate")
    assert callable(provider.generate)


@pytest.mark.asyncio
async def test_doubao_provider_interface():
    """Test Doubao provider has correct interface."""
    from nanobot.image.providers.doubao import DoubaoSeedreamProvider

    provider = DoubaoSeedreamProvider(api_key="test-key", model="doubao-seedream-4-5-251128")
    assert hasattr(provider, "generate")
    assert callable(provider.generate)


@pytest.mark.asyncio
async def test_image_tool_interface():
    """Test ImageGenerationTool has correct interface."""
    from nanobot.agent.tools.image import ImageGenerationTool
    from nanobot.image.providers.openai import OpenAIImageProvider

    provider = OpenAIImageProvider(api_key="test-key", model="dall-e-3")
    tool = ImageGenerationTool(provider)

    assert tool.name == "generate_image"
    assert "prompt" in tool.parameters["properties"]
    assert "size" in tool.parameters["properties"]
    assert tool.parameters["required"] == ["prompt"]
