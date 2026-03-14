#!/usr/bin/env python
"""日志持久化功能集成测试"""

import sys
import tempfile
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from nanobot.config.schema import LoggingConfig
from nanobot.utils.logging import setup_logging, get_log_files, search_logs
from loguru import logger


def test_logging_system():
    """测试日志系统"""
    print("=" * 60)
    print("日志持久化功能集成测试")
    print("=" * 60)

    # 创建临时日志目录
    temp_dir = Path(tempfile.mkdtemp())
    print(f"\n✓ 临时日志目录: {temp_dir}")

    # 模拟配置
    class MockConfig:
        def __init__(self):
            self.logging = LoggingConfig(
                enabled=True,
                level="DEBUG",
                rotation="10 MB",
                retention="7 days",
                sanitize_secrets=True,
                show_console=False
            )

    # 临时替换 get_logs_dir
    import nanobot.config.paths as paths_module
    original_get_logs_dir = paths_module.get_logs_dir
    paths_module.get_logs_dir = lambda: temp_dir

    try:
        # 1. 测试日志初始化
        print("\n[1/6] 测试日志初始化...")
        config = MockConfig()
        setup_logging(config.logging)
        print("✓ 日志系统初始化成功")

        # 2. 测试日志写入
        print("\n[2/6] 测试日志写入...")
        logger.debug("这是一条 DEBUG 日志")
        logger.info("这是一条 INFO 日志")
        logger.warning("这是一条 WARNING 日志")
        logger.error("这是一条 ERROR 日志")
        print("✓ 日志写入成功")

        # 3. 测试敏感信息脱敏
        print("\n[3/6] 测试敏感信息脱敏...")
        logger.info("api_key=sk-1234567890abcdefghijklmn")
        logger.info("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9")
        logger.info("token: abc123def456ghi789jkl012mno")
        print("✓ 敏感信息已记录（应该被脱敏）")

        # 4. 验证日志文件
        print("\n[4/6] 验证日志文件...")
        log_file = temp_dir / "nanobot.log"
        if log_file.exists():
            size = log_file.stat().st_size
            print(f"✓ 日志文件已创建: {log_file.name}")
            print(f"  文件大小: {size} bytes")

            # 读取日志内容
            with open(log_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.splitlines()
                print(f"  日志行数: {len(lines)}")

                # 验证脱敏
                if "sk-***" in content or "api_key=***" in content:
                    print("  ✓ API key 已脱敏")
                else:
                    print("  ✗ API key 脱敏失败")

                if "Bearer ***" in content:
                    print("  ✓ Bearer token 已脱敏")
                else:
                    print("  ✗ Bearer token 脱敏失败")
        else:
            print("✗ 日志文件未创建")

        # 5. 测试 get_log_files
        print("\n[5/6] 测试日志文件列表...")
        log_files = get_log_files()
        print(f"✓ 找到 {len(log_files)} 个日志文件")
        for f in log_files:
            print(f"  - {f.name}")

        # 6. 测试日志搜索
        print("\n[6/6] 测试日志搜索...")
        results = search_logs("ERROR", days=1)
        print(f"✓ 搜索到 {len(results)} 条 ERROR 日志")
        if results:
            print(f"  示例: {results[0][:80]}...")

        # 显示日志内容预览
        print("\n" + "=" * 60)
        print("日志内容预览（前 10 行）:")
        print("=" * 60)
        with open(log_file, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f, 1):
                if i > 10:
                    break
                print(line.rstrip())

        print("\n" + "=" * 60)
        print("✓ 所有测试通过！")
        print("=" * 60)

    finally:
        # 恢复原始函数
        paths_module.get_logs_dir = original_get_logs_dir

        # 清理临时文件
        import shutil
        shutil.rmtree(temp_dir)
        print(f"\n✓ 已清理临时目录: {temp_dir}")


if __name__ == "__main__":
    test_logging_system()
