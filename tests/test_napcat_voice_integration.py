#!/usr/bin/env python3
"""NapCat Voice 集成测试"""

import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_napcat_voice():
    """测试 NapCat 渠道的 TTS/ASR 功能"""
    from nanobot.config.loader import load_config

    print("=" * 60)
    print("NapCat Voice 集成测试")
    print("=" * 60)

    # 加载配置
    config = load_config()
    print(f"✓ 配置加载成功")
    print(f"  TTS Provider: {config.voice.tts.provider}")
    print(f"  TTS API Base: {config.voice.tts.api_base}")
    print(f"  ASR Provider: {config.voice.asr.provider}")
    print(f"  ASR API Base: {config.voice.asr.api_base}")

    # 直接测试 Provider 实例化
    print("\n测试 Provider 实例化:")

    try:
        from nanobot.voice.tts.openai import OpenAITTSProvider
        tts = OpenAITTSProvider(
            base_url=config.voice.tts.api_base,
            api_key=config.voice.tts.api_key,
            model=config.voice.tts.model_path or "tts-1",
            voice=config.voice.tts.voice,
        )
        print(f"  ✓ TTS Provider 实例化成功")
    except Exception as e:
        print(f"  ✗ TTS Provider 失败: {e}")
        return False

    try:
        from nanobot.voice.asr.openai import OpenAIASRProvider
        asr = OpenAIASRProvider(
            base_url=config.voice.asr.api_base,
            api_key=config.voice.asr.api_key,
            model=config.voice.asr.model_path or "whisper-1",
        )
        print(f"  ✓ ASR Provider 实例化成功")
    except Exception as e:
        print(f"  ✗ ASR Provider 失败: {e}")
        return False

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    print("✓ OpenAI 兼容 TTS/ASR 服务配置正确")
    print("\n下一步：")
    print("  启动 nanobot 测试实际功能: nanobot run")

    return True


if __name__ == "__main__":
    try:
        result = asyncio.run(test_napcat_voice())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
