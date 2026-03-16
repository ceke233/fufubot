"""OpenAI 兼容的 TTS Provider（通过 HTTP 调用）"""

import httpx
from loguru import logger

from nanobot.voice.base import TTSProvider


class OpenAITTSProvider(TTSProvider):
    """OpenAI 兼容的 TTS Provider

    支持调用 OpenAI 兼容的 TTS HTTP 服务（如本地 Qwen3-TTS 服务）
    """

    def __init__(self, base_url: str, api_key: str, model: str, voice: str):
        """初始化 OpenAI TTS Provider

        Args:
            base_url: API base URL (如 http://localhost:18000)
            api_key: API key（本地服务可为空）
            model: 模型名称（如 tts-1, tts-1-hd）
            voice: 默认音色（如 alloy, nova, shimmer）
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key or "dummy"
        self.model = model
        self.voice = voice
        logger.info(f"OpenAI TTS Provider 初始化: {base_url}, model={model}, voice={voice}")

    async def synthesize(
        self,
        text: str,
        voice: str | None = None,
        language: str = "Auto",
        **kwargs,
    ) -> tuple[bytes, int]:
        """合成语音

        Args:
            text: 要合成的文本
            voice: 音色（可选，默认使用初始化时的音色）
            language: 语言（OpenAI TTS 自动检测，此参数被忽略）
            **kwargs: 其他参数（如 speed）

        Returns:
            (音频数据, 采样率)
        """
        selected_voice = voice or self.voice
        speed = kwargs.get("speed", 1.0)

        logger.debug(f"OpenAI TTS 合成: text={text[:50]}..., voice={selected_voice}, speed={speed}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/v1/audio/speech",
                    json={
                        "model": self.model,
                        "input": text,
                        "voice": selected_voice,
                        "response_format": "wav",
                        "speed": speed,
                    },
                    headers={"Authorization": f"Bearer {self.api_key}"},
                )
                response.raise_for_status()
                audio_data = response.content

                logger.info(f"OpenAI TTS 合成成功: {len(audio_data)} bytes")
                return audio_data, 24000  # OpenAI API 不返回采样率，假设 24kHz

        except httpx.HTTPError as e:
            logger.error(f"OpenAI TTS 请求失败: {e}")
            raise RuntimeError(f"TTS 合成失败: {e}") from e
