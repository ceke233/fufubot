"""NapCat 文生图集成测试 - 生成图片并通过 QQ 发送"""

import asyncio
import os

import pytest


@pytest.mark.integration
@pytest.mark.skipif(
    not os.getenv("ARK_API_KEY") or not os.getenv("NAPCAT_ACCESS_TOKEN"),
    reason="Requires ARK_API_KEY and NAPCAT_ACCESS_TOKEN environment variables",
)
@pytest.mark.asyncio
async def test_napcat_send_generated_image():
    """测试通过 NapCat 发送 Doubao 生成的图片"""
    from nanobot.image.providers.doubao import DoubaoSeedreamProvider
    from nanobot.channels.napcat import NapCatChannel
    from nanobot.bus.queue import MessageBus
    from nanobot.config.schema import NapCatConfig

    # 1. 生成图片
    print("\n[1/3] 正在生成图片...")
    provider = DoubaoSeedreamProvider(
        api_key=os.getenv("ARK_API_KEY"),
        model="doubao-seedream-4-5-251128",
    )

    image_url = await provider.generate(
        prompt="一只可爱的猫娘工程师，坐在电脑前写代码，赛博朋克风格，高质量",
    )
    print(f"✓ 图片生成成功: {image_url}")

    # 2. 创建 NapCat 连接
    print("\n[2/3] 正在连接 NapCat...")
    config = NapCatConfig(
        enabled=True,
        ws_url="ws://127.0.0.1:3001",
        access_token=os.getenv("NAPCAT_ACCESS_TOKEN"),
        allow_from=[],
    )
    bus = MessageBus()
    channel = NapCatChannel(config, bus)

    # 3. 发送图片
    print("\n[3/3] 正在发送图片到 QQ...")

    async def send_image():
        from nanobot.bus.events import OutboundMessage

        # 在后台启动 channel
        start_task = asyncio.create_task(channel.start())
        await asyncio.sleep(3)  # 等待连接建立

        # 发送到指定 QQ 号
        test_user_id = os.getenv("TEST_QQ_USER_ID", "")
        if not test_user_id:
            pytest.skip("TEST_QQ_USER_ID not set")

        # 创建消息对象
        msg = OutboundMessage(
            channel="napcat",
            chat_id=test_user_id,
            content="浮浮酱生成的图片喵～",
            media=[image_url],
        )

        await channel.send(msg)
        print(f"✓ 图片已发送到 QQ: {test_user_id}")

        await asyncio.sleep(2)  # 等待发送完成

        # 停止 channel
        await channel.stop()
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass

    try:
        await asyncio.wait_for(send_image(), timeout=30)
    except asyncio.TimeoutError:
        pytest.skip("NapCat 连接超时，请确保 NapCat 已启动")
    except Exception as e:
        pytest.skip(f"测试跳过: {e}")


if __name__ == "__main__":
    asyncio.run(test_napcat_send_generated_image())
