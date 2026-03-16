#!/usr/bin/env python3
"""OpenAI 兼容 Voice 服务集成测试"""

import asyncio
import sys


async def test_tts():
    """测试 TTS 服务"""
    print("=" * 50)
    print("测试 OpenAI TTS Provider")
    print("=" * 50)

    from nanobot.voice.tts.openai import OpenAITTSProvider

    provider = OpenAITTSProvider(
        base_url="http://localhost:18000",
        api_key="",
        model="tts-1",
        voice="Vivian",  # 使用 Qwen3-TTS 支持的音色
    )

    try:
        text = "你好，我是浮浮酱，很高兴为你服务喵～"
        print(f"合成文本: {text}")

        audio_data, sample_rate = await provider.synthesize(text)

        print(f"✓ 合成成功!")
        print(f"  - 音频大小: {len(audio_data)} bytes")
        print(f"  - 采样率: {sample_rate} Hz")

        # 保存测试音频
        with open("/tmp/test_tts.wav", "wb") as f:
            f.write(audio_data)
        print(f"  - 已保存到: /tmp/test_tts.wav")

        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def test_asr():
    """测试 ASR 服务"""
    print("\n" + "=" * 50)
    print("测试 OpenAI ASR Provider")
    print("=" * 50)

    from nanobot.voice.asr.openai import OpenAIASRProvider

    provider = OpenAIASRProvider(
        base_url="http://localhost:18001",
        api_key="",
        model="whisper-1",
    )

    try:
        # 使用刚才生成的音频文件
        audio_file = "/tmp/test_tts.wav"
        print(f"转录文件: {audio_file}")

        text = await provider.transcribe(audio_file, language="Chinese")

        print(f"✓ 转录成功!")
        print(f"  - 识别文本: {text}")

        return True
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        return False


async def main():
    """主测试流程"""
    print("\n🎤 OpenAI 兼容 Voice 服务集成测试\n")

    # 测试 TTS
    tts_ok = await test_tts()

    # 测试 ASR
    asr_ok = await test_asr()

    # 总结
    print("\n" + "=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"TTS: {'✓ 通过' if tts_ok else '✗ 失败'}")
    print(f"ASR: {'✓ 通过' if asr_ok else '✗ 失败'}")

    if tts_ok and asr_ok:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print("\n❌ 部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
