"""OpenViking integration tests."""
from pathlib import Path

import pytest

from nanobot.agent.memory_viking import VikingMemoryStore


@pytest.mark.asyncio
async def test_viking_disabled_by_default():
    """Test that Viking is disabled when httpx is not available or config is not provided."""
    viking = VikingMemoryStore(
        workspace=Path("/tmp/test"),
        user_id="test_user",
        enabled=False
    )

    assert not viking.enabled
    assert viking.client is None

    # Should return False without error
    result = await viking.add_resource("test content")
    assert result is False

    # Should return empty list without error
    results = await viking.find("test query")
    assert results == []


@pytest.mark.asyncio
async def test_viking_memory_store_init():
    """Test VikingMemoryStore initialization."""
    viking = VikingMemoryStore(
        workspace=Path("/tmp/test"),
        user_id="test_user",
        base_url="http://localhost:1933",
        enabled=True,
        auto_recall=True,
        auto_capture=True
    )

    assert viking.user_id == "test_user"
    assert viking.base_url == "http://localhost:1933"
    assert viking.target_uri == "viking://user_test_user/memories"
    assert viking.auto_recall is True
    assert viking.auto_capture is True

    await viking.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_viking_add_resource(viking_server_url):
    """Test adding resource to OpenViking (requires running server)."""
    viking = VikingMemoryStore(
        workspace=Path("/tmp/test"),
        user_id="test_user",
        base_url=viking_server_url,
        enabled=True
    )

    try:
        success = await viking.add_resource(
            "Test memory content",
            {"type": "test", "timestamp": "2026-03-15"}
        )
        assert success is True
    finally:
        await viking.close()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_viking_semantic_search(viking_server_url):
    """Test semantic search in OpenViking (requires running server)."""
    viking = VikingMemoryStore(
        workspace=Path("/tmp/test"),
        user_id="test_user",
        base_url=viking_server_url,
        enabled=True
    )

    try:
        # Add some test data
        await viking.add_resource(
            "[2026-03-15] User likes cats and programming",
            {"type": "long_term"}
        )

        # Search for related content
        results = await viking.find("what does user like", max_results=5)
        assert isinstance(results, list)
        # Note: actual results depend on Viking server state
    finally:
        await viking.close()


@pytest.fixture
def viking_server_url():
    """Fixture for Viking server URL (skip if not available)."""
    import os
    url = os.getenv("VIKING_SERVER_URL", "http://localhost:1933")

    # Check if server is available
    try:
        import httpx
        response = httpx.get(f"{url}/health", timeout=2.0)
        if response.status_code == 200:
            return url
    except Exception:
        pass

    pytest.skip("OpenViking server not available")
