"""OpenViking integration for semantic memory retrieval."""
import time
from pathlib import Path
from typing import Optional, List, Dict, Any, TYPE_CHECKING
from loguru import logger

if TYPE_CHECKING:
    import httpx

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


class VikingMemoryStore:
    """OpenViking HTTP client for memory operations."""

    def __init__(
        self,
        workspace: Path,
        user_id: str,
        base_url: str = "http://localhost:1933",
        api_key: Optional[str] = None,
        enabled: bool = False,
        auto_recall: bool = True,
        auto_capture: bool = True,
        target_uri: Optional[str] = None,
        mode: str = "remote",
        config_path: Optional[str] = None
    ):
        self.workspace = workspace
        self.user_id = user_id
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.enabled = enabled and HTTPX_AVAILABLE
        self.auto_recall = auto_recall
        self.auto_capture = auto_capture
        self.mode = mode

        # 目标 URI：viking://user_{user_id}/memories
        self.target_uri = target_uri or f"viking://user_{user_id}/memories"

        # 简单的内存缓存
        self._cache: Dict[str, tuple[float, List[Dict]]] = {}
        self._cache_ttl = 300  # 5分钟缓存

        # 进程管理器（仅 local 模式）
        self.process_manager = None

        if self.enabled:
            # Local 模式：自动启动服务器
            if mode == "local":
                from nanobot.agent.viking_process import VikingProcessManager
                self.process_manager = VikingProcessManager(
                    config_path or "~/.openviking/ov.conf",
                    port=int(base_url.split(":")[-1]) if ":" in base_url else 1933
                )
                if not self.process_manager.start():
                    logger.error("Failed to start OpenViking server, disabling integration")
                    self.enabled = False
                    self.process_manager = None

            # 创建 HTTP 客户端
            if self.enabled:
                headers = {"X-API-Key": api_key} if api_key else {}
                self.client: Optional["httpx.AsyncClient"] = httpx.AsyncClient(
                    base_url=self.base_url,
                    timeout=30.0,
                    headers=headers
                )
                logger.info(f"VikingMemoryStore enabled for {user_id} at {self.base_url}")
            else:
                self.client: Optional["httpx.AsyncClient"] = None
        else:
            self.client: Optional["httpx.AsyncClient"] = None
            if not HTTPX_AVAILABLE:
                logger.warning("httpx not available, VikingMemoryStore disabled")

    async def add_resource(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Add memory content to OpenViking."""
        if not self.enabled or not self.auto_capture or not self.client:
            return False

        try:
            response = await self.client.post(
                "/api/v1/resources",
                json={
                    "uri": self.target_uri,
                    "content": content,
                    "metadata": metadata or {}
                }
            )
            response.raise_for_status()
            logger.debug(f"Memory synced to {self.target_uri}")
            return True
        except Exception as e:
            logger.error(f"Failed to add resource to Viking: {e}")
            return False

    async def find(self, query: str, max_results: int = 5) -> List[Dict]:
        """Semantic search in memories with caching."""
        if not self.enabled or not self.auto_recall or not self.client:
            return []

        # 检查缓存
        cache_key = f"{query}:{max_results}"
        if cache_key in self._cache:
            cached_time, cached_results = self._cache[cache_key]
            if time.time() - cached_time < self._cache_ttl:
                logger.debug(f"Cache hit for query: {query[:50]}")
                return cached_results

        # 执行搜索
        try:
            response = await self.client.post(
                "/api/v1/find",
                json={
                    "uri": self.target_uri,
                    "query": query,
                    "limit": max_results
                },
                timeout=5.0  # 快速超时
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            logger.debug(f"Found {len(results)} memories for query: {query[:50]}")

            # 更新缓存
            self._cache[cache_key] = (time.time(), results)
            return results
        except Exception as e:
            logger.warning(f"Viking search failed, falling back: {e}")
            return []

    def rank_memories(self, results: List[Dict], query: str) -> List[Dict]:
        """Re-rank memories based on relevance and recency."""
        import re
        from datetime import datetime

        for result in results:
            score = result.get("score", 0.0)

            # 时间衰减：最近的记忆权重更高
            timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2})', result.get("content", ""))
            if timestamp_match:
                date_str = timestamp_match.group(1)
                try:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                    days_ago = (datetime.now() - date).days
                    time_decay = 1.0 / (1.0 + days_ago / 30.0)  # 30天半衰期
                    score *= time_decay
                except:
                    pass

            # 关键词匹配加权
            query_keywords = set(query.lower().split())
            content_keywords = set(result.get("content", "").lower().split())
            keyword_overlap = len(query_keywords & content_keywords) / max(len(query_keywords), 1)
            score *= (1.0 + keyword_overlap)

            result["final_score"] = score

        # 按最终得分排序
        return sorted(results, key=lambda x: x.get("final_score", 0), reverse=True)

    async def close(self):
        """Close HTTP client and stop server if in local mode."""
        if self.client:
            await self.client.aclose()
        if self.process_manager:
            self.process_manager.stop()

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):  # type: ignore
        """Context manager exit with cleanup."""
        await self.close()
