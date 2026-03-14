"""日志系统初始化模块"""

from loguru import logger
from pathlib import Path
import re
import sys


def setup_logging(config):
    """配置 loguru 日志系统（简化版：单文件）"""
    from nanobot.config.paths import get_logs_dir

    logs_dir = get_logs_dir()
    logs_dir.mkdir(parents=True, exist_ok=True)

    # 移除默认 handler
    logger.remove()

    # 终端输出（可选）
    if config.show_console:
        logger.add(
            sys.stderr,
            level=config.level,
            format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
        )

    # 单一日志文件（所有级别）
    logger.add(
        logs_dir / "nanobot.log",
        level=config.level,
        rotation=config.rotation,
        retention=config.retention,
        compression=config.compression,
        enqueue=True,
        backtrace=True,
        diagnose=True,
        filter=sanitize_filter if config.sanitize_secrets else None,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    logger.info(f"日志系统已初始化：{logs_dir / 'nanobot.log'}")


def sanitize_filter(record):
    """脱敏敏感信息"""
    message = record["message"]

    message = re.sub(r'(api[_-]?key["\s:=]+)([a-zA-Z0-9_-]{20,})', r'\1***', message, flags=re.IGNORECASE)
    message = re.sub(r'Bearer\s+[a-zA-Z0-9_.-]+', 'Bearer ***', message)
    message = re.sub(r'sk-[a-zA-Z0-9]{20,}', 'sk-***', message)
    message = re.sub(r'(token["\s:=]+)([a-zA-Z0-9_.-]{20,})', r'\1***', message, flags=re.IGNORECASE)

    record["message"] = message
    return True


def get_log_files() -> list[Path]:
    """获取所有日志文件"""
    from nanobot.config.paths import get_logs_dir
    logs_dir = get_logs_dir()
    return sorted(logs_dir.glob("nanobot*.log*"), reverse=True)


def search_logs(pattern: str, days: int = 7) -> list[str]:
    """搜索日志内容"""
    from datetime import datetime, timedelta

    results = []
    cutoff = datetime.now() - timedelta(days=days)

    for log_file in get_log_files():
        # 检查文件修改时间
        if log_file.stat().st_mtime < cutoff.timestamp():
            continue

        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if re.search(pattern, line, re.IGNORECASE):
                    results.append(f"{log_file.name}: {line.strip()}")

    return results
