"""OpenAI 兼容的 ASR Provider（通过 HTTP 调用）"""

import httpx
from io import BytesIO
from loguru import logger

from nanobot.voice.base import ASRProvider


class OpenAIASRProvider(ASRProvider):
    """OpenAI 兼容的 ASR Provider

    支持调用 OpenAI 兼容的 ASR HTTP 服务（如本地 Qwen3-ASR 服务）
    """

    def __init__(self, base_url: str, api_key: str, model: str):
        """初始化 OpenAI ASR Provider

        Args:
            base_url: API base URL (如 http://localhost:18001)
            api_key: API key（本地服务可为空）
            model: 模型名称（如 whisper-1）
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "dummy"
        self.model = model
        logger.info(f"OpenAI ASR Provider 初始化: {base_url}, model={model}")

    async def transcribe(
        self,
        audio: bytes | str,
        language: str | None = None,
        **kwargs,
    ) -> str:
        """转录音频

        Args:
            audio: 音频数据（bytes）或文件路径（str）
            language: 语言代码（可选，如 zh, en）
            **kwargs: 其他参数

        Returns:
            转录文本
        """
        logger.debug(f"OpenAI ASR 转录: audio_type={type(audio).__name__}, language={language}")

        # 准备文件数据
        if isinstance(audio, bytes):
            files = {"file": ("audio.wav", BytesIO(audio), "audio/wav")}
            file_handle = None
        else:
            file_handle = open(audio, "rb")
            files = {"file": file_handle}

        try:
            # 准备表单数据
            data = {"model": self.model}
            if language:
                data["language"] = language

            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/audio/transcriptions",
                    files=files,
                    data=data,
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                result = response.json()
                text = result["text"]

                logger.info(f"OpenAI ASR 转录成功: {text[:100]}...")
                return text

        except httpx.HTTPError as e:
            logger.error(f"OpenAI ASR 请求失败: {e}")
            raise RuntimeError(f"ASR 转录失败: {e}") from e
        finally:
            # 关闭文件句柄
            if file_handle:
                file_handle.close()
