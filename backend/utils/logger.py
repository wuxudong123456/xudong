"""
统一日志配置模块
提供分级日志、按天轮转、多处理器支持
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path

from backend.config import settings


def setup_logging(
    log_dir: str = "logs",
    app_name: str = None,
    log_level: str = "INFO",
    console_output: bool = True,
) -> logging.Logger:
    """
    初始化应用日志系统
    :param log_dir: 日志文件存放目录
    :param app_name: 应用名称（用于日志文件名）
    :param log_level: 日志级别 DEBUG/INFO/WARNING/ERROR
    :param console_output: 是否同时输出到控制台
    :return: 配置好的根日志记录器
    """
    app_name = app_name or settings.APP_NAME or "app"
    log_dir_path = Path(log_dir)
    log_dir_path.mkdir(parents=True, exist_ok=True)

    # 根记录器
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # 清除已有处理器（避免重复）
    if root_logger.handlers:
        root_logger.handlers.clear()

    # 统一格式
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 文件处理器 - 按天轮转，保留30天
    log_file = log_dir_path / f"{app_name}.log"
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(log_file),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    file_handler.suffix = "%Y-%m-%d"
    root_logger.addHandler(file_handler)

    # 错误日志单独文件
    error_file = log_dir_path / f"{app_name}_error.log"
    error_handler = logging.handlers.TimedRotatingFileHandler(
        filename=str(error_file),
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    error_handler.suffix = "%Y-%m-%d"
    root_logger.addHandler(error_handler)

    # 控制台处理器
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 设置第三方库日志级别（减少噪音）
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """获取指定名称的日志记录器"""
    return logging.getLogger(name)
