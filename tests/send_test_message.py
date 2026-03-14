#!/usr/bin/env python3
"""向指定 QQ 发送测试消息"""

import asyncio
from nanobot.channels.napcat import NapCatChannel
from nanobot.bus.queue import MessageBus
from nanobot.bus.events import OutboundMessage
from nanobot.config.schema import NapCatConfig

# 配置
CONFIG = {
    "ws_url": "ws://127.0.0.1:3001",
    "access_token": "123456789123",
    "allow_from": [],
    "group_policy": "mention",
    "handle_notice_events": True,
    "handle_request_events": True,
    "auto_approve_friend": False
}

TARGET_QQ = "YOUR_QQ_NUMBER"  # 替换为目标 QQ 号
MESSAGE = "测试消息"
MEDIA_FILES = [
    # "/path/to/your/media/file.wav"  # 可选：添加媒体文件路径
]


async def send_message():
    """发送消息"""
    config = NapCatConfig(**CONFIG)
    bus = MessageBus()
    channel = NapCatChannel(config, bus)

    print(f"正在连接 NapCat...")

    # 启动 channel（在后台）
    task = asyncio.create_task(channel.start())

    # 等待连接建立
    await asyncio.sleep(2)

    if not channel._ws:
        print("✗ 连接失败")
        return

    print(f"✓ 连接成功")
    print(f"正在发送消息到 QQ {TARGET_QQ}...")

    # 发送消息（带图片和音频）
    msg = OutboundMessage(
        channel="napcat",
        chat_id=TARGET_QQ,
        content=MESSAGE,
        media=MEDIA_FILES,
        metadata={"is_group": False}
    )

    await channel.send(msg)
    print(f"✓ 消息已发送")

    # 等待一下确保消息发送完成
    await asyncio.sleep(1)

    # 停止 channel
    await channel.stop()
    task.cancel()

    print("✓ 完成")


if __name__ == "__main__":
    asyncio.run(send_message())
