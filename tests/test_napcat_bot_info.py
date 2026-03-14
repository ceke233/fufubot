#!/usr/bin/env python3
"""测试 NapCat 连接并获取 bot 信息"""

import asyncio
import json
import websockets


async def test_napcat_connection():
    """测试连接 NapCat 并获取 bot 信息"""
    ws_url = "ws://localhost:3001"
    access_token = "123456789123"  # 从 send_test_message.py 获取

    print(f"🔗 连接到 {ws_url}...")

    try:
        headers = {}
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
            print(f"🔑 使用 access_token")

        async with websockets.connect(ws_url, additional_headers=headers) as ws:
            print("✅ WebSocket 连接成功！")

            # 先监听一下是否有初始消息
            print("\n👂 监听初始消息...")
            try:
                initial_msg = await asyncio.wait_for(ws.recv(), timeout=2.0)
                print(f"📨 收到初始消息: {initial_msg[:200]}")
            except asyncio.TimeoutError:
                print("⏱️  没有初始消息（正常）")

            # 等待 NapCat 初始化
            await asyncio.sleep(1)

            # 发送 get_login_info 请求
            request = {
                "action": "get_login_info",
                "params": {},
                "echo": "test_echo_1"
            }

            print(f"\n📤 发送请求: {json.dumps(request, ensure_ascii=False)}")
            await ws.send(json.dumps(request))

            # 等待响应
            print("\n⏳ 等待响应...")
            response = await asyncio.wait_for(ws.recv(), timeout=10.0)

            print(f"\n📥 收到响应:")
            data = json.loads(response)
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # 解析 bot 信息
            if data.get("status") == "ok":
                bot_info = data.get("data", {})
                user_id = bot_info.get("user_id")
                nickname = bot_info.get("nickname")

                print(f"\n✨ Bot 信息:")
                print(f"   QQ 号: {user_id}")
                print(f"   昵称: {nickname}")

                if user_id:
                    print(f"\n✅ 成功获取 bot_qq = {user_id}")
                else:
                    print(f"\n❌ 响应中没有 user_id 字段")
            else:
                print(f"\n❌ API 调用失败: {data.get('msg')}")

    except asyncio.TimeoutError:
        print("\n❌ 连接超时")
    except ConnectionRefusedError:
        print(f"\n❌ 连接被拒绝，请确认 NapCat 在 {ws_url} 运行")
    except Exception as e:
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    asyncio.run(test_napcat_connection())
