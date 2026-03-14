#!/usr/bin/env python3
"""NapCat Channel 集成测试脚本"""

import asyncio
import json
from pathlib import Path

# 测试配置
TEST_CONFIG = {
    "ws_url": "ws://127.0.0.1:3001",
    "access_token": "YOUR_TOKEN_HERE",  # 如果 NapCat 配置了 token 就填写
    "allow_from": [],  # 空列表表示允许所有用户
    "group_policy": "mention",
    "handle_notice_events": True,
    "handle_request_events": True,
    "auto_approve_friend": False
}


async def test_napcat_connection():
    """测试 NapCat 连接"""
    print("=" * 60)
    print("NapCat Channel 集成测试")
    print("=" * 60)

    try:
        from nanobot.channels.napcat import NapCatChannel
        from nanobot.bus.queue import MessageBus
        from nanobot.config.schema import NapCatConfig

        # 创建配置
        config = NapCatConfig(**TEST_CONFIG)
        bus = MessageBus()

        # 创建 channel
        channel = NapCatChannel(config, bus)

        print("\n✓ NapCat Channel 创建成功")
        print(f"  WebSocket URL: {config.ws_url}")
        print(f"  群组策略: {config.group_policy}")
        print(f"  处理通知事件: {config.handle_notice_events}")
        print(f"  处理请求事件: {config.handle_request_events}")

        # 测试连接（5秒超时）
        print("\n正在连接 NapCat...")
        print("提示：请确保 NapCat 已启动并监听在 ws://127.0.0.1:3001")

        try:
            await asyncio.wait_for(
                test_connection_only(channel),
                timeout=5.0
            )
        except asyncio.TimeoutError:
            print("\n✗ 连接超时（5秒）")
            print("  请检查：")
            print("  1. NapCat 是否已启动")
            print("  2. WebSocket 端口是否正确（默认 3001）")
            print("  3. 防火墙是否阻止连接")
            return False

    except ImportError as e:
        print(f"\n✗ 导入失败: {e}")
        print("  请确保已安装依赖: pip install websockets httpx")
        return False
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        return False

    return True


async def test_connection_only(channel):
    """仅测试连接，不持续运行"""
    import websockets

    try:
        headers = {}
        if channel.config.access_token:
            headers["Authorization"] = f"Bearer {channel.config.access_token}"

        async with websockets.connect(
            channel.config.ws_url,
            additional_headers=headers,
        ) as ws:
            print("✓ WebSocket 连接成功")

            # 测试 API 调用
            echo = "test_echo"
            request = {
                "action": "get_login_info",
                "params": {},
                "echo": echo
            }

            await ws.send(json.dumps(request))
            print("✓ 发送 API 请求成功")

            # 等待响应（可能会先收到 lifecycle 事件）
            for _ in range(3):  # 最多尝试 3 次
                response = await asyncio.wait_for(ws.recv(), timeout=3.0)
                data = json.loads(response)

                # 跳过 meta_event
                if data.get("post_type") == "meta_event":
                    continue

                # 检查是否是我们的 API 响应
                if data.get("echo") == echo and data.get("status") == "ok":
                    bot_info = data.get("data", {})
                    bot_qq = bot_info.get("user_id")
                    nickname = bot_info.get("nickname", "未知")

                    print(f"✓ 获取机器人信息成功")
                    print(f"  机器人 QQ: {bot_qq}")
                    print(f"  昵称: {nickname}")

                    print("\n" + "=" * 60)
                    print("✓ 所有测试通过！")
                    print("=" * 60)
                    print("\n现在你可以：")
                    print("1. 向机器人发送文字消息测试")
                    print("2. 向机器人发送图片消息测试")
                    print("3. 向机器人发送语音消息测试（需配置 Groq API Key）")
                    print("4. 在群聊中 @机器人 测试群聊功能")
                    return True

            print(f"✗ 未收到有效的 API 响应")
            return False

    except websockets.exceptions.WebSocketException as e:
        print(f"✗ WebSocket 连接失败: {e}")
        raise
    except asyncio.TimeoutError:
        print("✗ API 响应超时")
        raise
    except Exception as e:
        print(f"✗ 未知错误: {e}")
        raise


if __name__ == "__main__":
    print("\n提示：按 Ctrl+C 可随时退出测试\n")

    try:
        asyncio.run(test_napcat_connection())
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n测试异常: {e}")
