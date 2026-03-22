"""OpenAI 兼容 TTS/ASR 集成测试"""

import pytest
import httpx


@pytest.mark.asyncio
async def test_openai_tts_provider():
    """测试 OpenAI TTS Provider"""
    from nanobot.voice.tts.openai import OpenAITTSProvider

    provider = OpenAITTSProvider(
        base_url="http://localhost:18000",
        api_key="",
        model="tts-1",
        voice="alloy",
    )

    # 测试合成
    try:
        audio_data, sample_rate = await provider.synthesize("你好，世界")
        assert isinstance(audio_data, bytes)
        assert len(audio_data) > 0
        assert sample_rate == 24000
        print(f"✓ TTS 合成成功: {len(audio_data)} bytes, {sample_rate} Hz")
    except httpx.HTTPError as e:
        pytest.skip(f"TTS 服务未运行: {e}")


@pytest.mark.asyncio
async def test_openai_asr_provider():
    """测试 OpenAI ASR Provider"""
    from nanobot.voice.asr.openai import OpenAIASRProvider

    provider = OpenAIASRProvider(
        base_url="http://localhost:18001",
        api_key="",
        model="whisper-1",
    )

    # 创建测试音频（需要真实音频文件）
    test_audio = b"RIFF" + b"\x00" * 100  # 假音频数据

    try:
        text = await provider.transcribe(test_audio, language="zh")
        assert isinstance(text, str)
        print(f"✓ ASR 转录成功: {text}")
    except httpx.HTTPError as e:
        pytest.skip(f"ASR 服务未运行: {e}")


if __name__ == "__main__":
    import asyncio

    print("测试 OpenAI TTS Provider...")
    asyncio.run(test_openai_tts_provider())

    print("\n测试 OpenAI ASR Provider...")
    asyncio.run(test_openai_asr_provider())
