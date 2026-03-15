"""OpenViking server process manager for local mode."""
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Optional
from loguru import logger


class VikingProcessManager:
    """Manage OpenViking server process in local mode."""

    def __init__(self, config_path: str = "~/.openviking/ov.conf", port: int = 1933):
        self.config_path = Path(config_path).expanduser()
        self.process: Optional[subprocess.Popen] = None
        self.port = port

    def start(self) -> bool:
        """Start OpenViking server."""
        if not self.config_path.exists():
            logger.error(f"OpenViking config not found: {self.config_path}")
            return False

        try:
            # 检查端口是否已被占用
            if self._is_port_in_use():
                logger.info(f"OpenViking server already running on port {self.port}")
                return True

            # 启动服务器
            env = os.environ.copy()
            env["OPENVIKING_CONFIG_FILE"] = str(self.config_path)

            self.process = subprocess.Popen(
                ["openviking-server"],
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                start_new_session=True  # 独立进程组
            )

            # 等待服务器启动
            if self._wait_for_ready(timeout=30):
                logger.info(f"OpenViking server started (PID: {self.process.pid})")
                return True
            else:
                logger.error("OpenViking server failed to start")
                self.stop()
                return False

        except Exception as e:
            logger.error(f"Failed to start OpenViking server: {e}")
            return False

    def stop(self):
        """Stop OpenViking server."""
        if self.process:
            try:
                # 优雅关闭
                self.process.terminate()
                self.process.wait(timeout=5)
                logger.info("OpenViking server stopped")
            except subprocess.TimeoutExpired:
                # 强制关闭
                self.process.kill()
                logger.warning("OpenViking server force killed")
            finally:
                self.process = None

    def _is_port_in_use(self) -> bool:
        """Check if port is in use."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("localhost", self.port)) == 0

    def _wait_for_ready(self, timeout: int = 30) -> bool:
        """Wait for server to be ready."""
        try:
            import httpx
        except ImportError:
            logger.warning("httpx not available, cannot check server readiness")
            time.sleep(5)  # 简单等待
            return True

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = httpx.get(f"http://localhost:{self.port}/health", timeout=2.0)
                if response.status_code == 200:
                    return True
            except:
                pass
            time.sleep(1)
        return False
