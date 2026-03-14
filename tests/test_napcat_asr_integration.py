#!/usr/bin/env python3
"""NapCat 语音消息 ASR 集成测试"""

import asyncio
import json
import os
from pathlib import Path

# 测试配置
TEST_CONFIG = {
    "ws_url": "ws://127.0.0.1:3001",
    "access_token": os.getenv("NAPCAT_ACCESS_TOKEN", ""),
    "python_path": "/home/ceke233/miniconda3/envs/qwen3-asr-tts/bin/python",
    "asr_model_path": "/mnt/f/CodeProject/models/Qwen3-ASR-1.7B",
}


async def test_napcat_voice_to_asr():
    """测试 NapCat 接收语音消息并通过 ASR 转换为文本"""
    print("=" * 60)
    print("NapCat 语音消息 ASR 集成测试")
    print("=" * 60)

    try:
        from nanobot.config.schema import NapCatConfig
        from nanobot.voice.asr.qwen import QwenASRProvider

        # 创建 ASR Provider
        print("\n初始化 ASR Provider...")
        asr_provider = QwenASRProvider(
            python_path=TEST_CONFIG["python_path"],
            model_path=TEST_CONFIG["asr_model_path"],
            device="cpu"
        )
        print(f"✓ ASR Provider 初始化成功")
        print(f"  模型路径: {asr_provider.model_path}")
        print(f"  设备: {asr_provider.device}")

        # 创建 NapCat Channel
        print("\n初始化 NapCat Channel...")
        config = NapCatConfig(
            ws_url=TEST_CONFIG["ws_url"],
            access_token=TEST_CONFIG["access_token"],
            allow_from=["*"],
            group_policy="open",
            voice_enabled=True,
            asr_enabled=True
        )
        print("✓ NapCat Channel 初始化成功")
        print(f"  WebSocket URL: {config.ws_url}")

        # 测试语音消息处理
        print("\n" + "=" * 60)
        print("等待语音消息...")
        print("=" * 60)
        print("请向机器人发送一条语音消息进行测试")
        print("提示：按 Ctrl+C 可退出测试\n")

        # 启动 channel 并监听消息
        async def process_voice_message():
            import websockets
            import httpx

            headers = {}
            if config.access_token:
                headers["Authorization"] = f"Bearer {config.access_token}"

            async with websockets.connect(config.ws_url, additional_headers=headers) as ws:
                print("✓ WebSocket 连接成功，等待语音消息...\n")

                while True:
                    message = await ws.recv()
                    data = json.loads(message)

                    # 跳过非消息事件
                    if data.get("post_type") != "message":
                        continue

                    # 检查是否包含语音消息
                    message_data = data.get("message", [])
                    voice_segment = None

                    for segment in message_data:
                        if segment.get("type") == "record":
                            voice_segment = segment
                            break

                    if not voice_segment:
                        continue

                    # 找到语音消息
                    print("✓ 收到语音消息")
                    file_id = voice_segment.get("data", {}).get("file")
                    print(f"  文件 ID: {file_id}")

                    # 获取语音文件 URL
                    echo = "get_record"
                    request = {
                        "action": "get_record",
                        "params": {"file": file_id, "out_format": "wav"},
                        "echo": echo
                    }
                    await ws.send(json.dumps(request))

                    # 等待响应
                    for _ in range(5):
                        response = await asyncio.wait_for(ws.recv(), timeout=5.0)
                        resp_data = json.loads(response)

                        if resp_data.get("echo") == echo and resp_data.get("status") == "ok":
                            file_path = resp_data.get("data", {}).get("file")
                            print(f"✓ 获取语音文件路径: {file_path}")

                            # 下载或读取语音文件
                            temp_file = Path("test_voice_input.wav")

                            if file_path.startswith(("http://", "https://")):
                                # HTTP URL - 下载文件
                                async with httpx.AsyncClient() as client:
                                    resp = await client.get(file_path)
                                    temp_file.write_bytes(resp.content)
                                print(f"✓ 下载语音文件: {temp_file}")
                            else:
                                # 本地文件路径 - 直接复制
                                import shutil
                                shutil.copy(file_path, temp_file)
                                print(f"✓ 复制语音文件: {temp_file}")

                            # ASR 转换
                            print("\n开始 ASR 转换...")
                            transcribed_text = await asr_provider.transcribe(
                                audio=str(temp_file),
                                language="Chinese"
                            )

                            print("\n" + "=" * 60)
                            print("✓ ASR 转换成功！")
                            print("=" * 60)
                            print(f"识别结果: {transcribed_text}")
                            print("=" * 60)

                            # 清理临时文件
                            temp_file.unlink(missing_ok=True)
                            return True

        await asyncio.wait_for(process_voice_message(), timeout=300.0)

    except asyncio.TimeoutError:
        print("\n✗ 测试超时（5分钟）")
        print("  未收到语音消息")
        return False
    except ImportError as e:
        print(f"\n✗ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True


if __name__ == "__main__":
    print("\n提示：按 Ctrl+C 可随时退出测试\n")

    try:
        asyncio.run(test_napcat_voice_to_asr())
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n测试异常: {e}")
