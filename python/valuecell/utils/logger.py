"""日志配置模块 - 统一配置 loguru 日志输出"""

import os
import sys
from pathlib import Path

from loguru import logger

from .env import get_system_env_dir


def get_log_dir() -> Path:
    """获取日志目录路径

    优先级：
    1. LOG_DIR 环境变量
    2. 系统环境目录下的 logs 子目录

    Returns:
        日志目录路径
    """
    # 从环境变量获取日志目录
    log_dir_env = os.getenv("LOG_DIR")
    if log_dir_env:
        return Path(log_dir_env)

    # 默认使用系统环境目录下的 logs 子目录
    return get_system_env_dir() / "logs"


def setup_logger(
        log_level: str = "INFO",
        log_dir: Path = None,
        rotation: str = "10 MB",
        retention: str = "30 days",
        compression: str = "zip",
        enable_console: bool = True,
        enable_file: bool = True,
) -> None:
    """配置 loguru 日志

    Args:
        log_level: 日志级别，默认 INFO
        log_dir: 日志目录，默认使用 get_log_dir()
        rotation: 日志轮转规则，默认 10 MB
        retention: 日志保留时间，默认 30 天
        compression: 日志压缩格式，默认 zip
        enable_console: 是否启用控制台输出，默认 True
        enable_file: 是否启用文件输出，默认 True
    """
    # 从环境变量读取配置
    log_level = os.getenv("LOG_LEVEL", log_level).upper()
    rotation = os.getenv("LOG_ROTATION", rotation)
    retention = os.getenv("LOG_RETENTION", retention)

    # 移除默认的 handler
    logger.remove()

    # 添加控制台输出
    if enable_console:
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
            level=log_level,
            colorize=True,
        )

    # 添加文件输出
    if enable_file:
        # 确定日志目录
        if log_dir is None:
            log_dir = get_log_dir()

        # 创建日志目录
        log_dir.mkdir(parents=True, exist_ok=True)

        # 所有日志文件（包含DEBUG及以上）
        logger.add(
            log_dir / "valuecell_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            level="DEBUG",
            rotation=rotation,
            retention=retention,
            compression=compression,
            encoding="utf-8",
            enqueue=True,  # 异步写入，避免阻塞
        )

        # 错误日志单独文件（只包含ERROR及以上）
        logger.add(
            log_dir / "error_{time:YYYY-MM-DD}.log",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}\n{exception}",
            level="ERROR",
            rotation=rotation,
            retention=retention,
            compression=compression,
            encoding="utf-8",
            enqueue=True,
            backtrace=True,  # 显示完整堆栈
            diagnose=True,  # 显示变量值
        )

        logger.info(f"日志文件输出目录: {log_dir}")

    logger.debug(f"日志配置完成 - 级别: {log_level}, 控制台: {enable_console}, 文件: {enable_file}")


def get_logger():
    """获取 logger 实例

    Returns:
        loguru logger 实例
    """
    return logger
