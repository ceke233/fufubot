"""Test image tool registration in AgentLoop."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

from nanobot.agent.loop import AgentLoop
from nanobot.bus.queue import MessageBus


@pytest.mark.asyncio
async def test_image_tool_registration_openai():
    """Test image tool is registered when enabled with OpenAI provider."""
    bus = MessageBus()
    provider = MagicMock()
    provider.get_default_model = MagicMock(return_value="gpt-4")
    workspace = Path("/tmp/test_workspace")

    image_config = {
        "enabled": True,
        "provider": "openai",
        "model": "dall-e-3",
        "api_key": "test-key",
    }

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=workspace,
        image_config=image_config,
    )

    # Check tool is registered
    assert "generate_image" in agent.tools._tools
    tool = agent.tools._tools["generate_image"]
    assert tool.name == "generate_image"


@pytest.mark.asyncio
async def test_image_tool_registration_dashscope():
    """Test image tool is registered when enabled with DashScope provider."""
    bus = MessageBus()
    provider = MagicMock()
    provider.get_default_model = MagicMock(return_value="gpt-4")
    workspace = Path("/tmp/test_workspace")

    image_config = {
        "enabled": True,
        "provider": "dashscope",
        "model": "wanx-v1",
        "api_key": "test-key",
    }

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=workspace,
        image_config=image_config,
    )

    # Check tool is registered
    assert "generate_image" in agent.tools._tools
    tool = agent.tools._tools["generate_image"]
    assert tool.name == "generate_image"


@pytest.mark.asyncio
async def test_image_tool_registration_doubao():
    """Test image tool is registered when enabled with Doubao provider."""
    bus = MessageBus()
    provider = MagicMock()
    provider.get_default_model = MagicMock(return_value="gpt-4")
    workspace = Path("/tmp/test_workspace")

    image_config = {
        "enabled": True,
        "provider": "doubao",
        "model": "doubao-seedream-4-5-251128",
        "api_key": "test-key",
    }

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=workspace,
        image_config=image_config,
    )

    # Check tool is registered
    assert "generate_image" in agent.tools._tools
    tool = agent.tools._tools["generate_image"]
    assert tool.name == "generate_image"


@pytest.mark.asyncio
async def test_image_tool_not_registered_when_disabled():
    """Test image tool is NOT registered when disabled."""
    bus = MessageBus()
    provider = MagicMock()
    provider.get_default_model = MagicMock(return_value="gpt-4")
    workspace = Path("/tmp/test_workspace")

    image_config = {
        "enabled": False,
    }

    agent = AgentLoop(
        bus=bus,
        provider=provider,
        workspace=workspace,
        image_config=image_config,
    )

    # Check tool is NOT registered
    assert "generate_image" not in agent.tools._tools
