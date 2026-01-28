"""Logging utilities for funcguard."""

import logging
import os
import sys
from typing import Optional, TextIO, Union, cast


def _supports_ansi(stream: Optional[TextIO] = None) -> bool:
    """
    检测流是否支持 ANSI 颜色代码。

    Args:
        stream: 要检测的流，默认为 sys.stdout

    Returns:
        如果流支持 ANSI 颜色代码则返回 True，否则返回 False
    """
    if stream is None:
        stream = sys.stdout

    # 检查是否被强制禁用颜色
    if os.environ.get("NO_COLOR"):
        return False

    # 检查是否被强制启用颜色
    if os.environ.get("FORCE_COLOR"):
        return True

    # 如果不是终端（TTY），不支持 ANSI
    if not hasattr(stream, "isatty") or not stream.isatty():
        return False

    # Windows 需要特殊处理
    if sys.platform == "win32":
        # Windows 10 build 14393+ 支持 ANSI，尝试启用
        try:
            # 调用 os.system("") 可以启用 Windows 10+ 的 ANSI 支持
            os.system("")
            return True
        except Exception:
            return False

    # Unix-like 系统默认支持 ANSI
    return True


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器。

    自动检测终端是否支持 ANSI 颜色代码：
    - 如果输出不是终端（TTY），则不添加颜色代码
    - 在 Windows 上自动启用 ANSI 支持（Windows 10+）
    - 支持 NO_COLOR 和 FORCE_COLOR 环境变量
    """

    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[37m",  # 白色/浅灰色/默认
        "PROGRESS": "\033[34m",  # 蓝色
        "SUCCESS": "\033[32m",  # 绿色
        "WARNING": "\033[33m",  # 黄色
        "ERROR": "\033[31m",  # 红色
        "CRITICAL": "\033[35m",  # 紫色
        "RESET": "\033[0m",  # 重置所有颜色
    }

    def __init__(
        self,
        fmt: Optional[str] = None,
        datefmt: Optional[str] = None,
        style: str = "%",
        stream: Optional[TextIO] = None,
    ):
        super().__init__(fmt, datefmt, style)
        self._stream = stream
        self._use_colors: Optional[bool] = None

    def _should_use_colors(self, stream: Optional[TextIO] = None) -> bool:
        """判断是否应该使用颜色。"""
        # 如果已经检测过，直接返回缓存结果
        if self._use_colors is not None:
            return self._use_colors

        # 使用传入的 stream 或初始化时的 stream
        check_stream = stream or self._stream
        self._use_colors = _supports_ansi(check_stream)
        return self._use_colors

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if self._should_use_colors():
            color = self.COLORS.get(record.levelname, self.COLORS["INFO"])
            return f"{color}{message}{self.COLORS['RESET']}"
        return message


def _has_colored_handler(logger: logging.Logger) -> bool:
    """
    检查 logger 是否已配置彩色 StreamHandler。

    用于避免重复添加 handler，防止同一条日志被多次输出。
    """
    for handler in logger.handlers:
        if isinstance(handler, logging.StreamHandler) and isinstance(
            handler.formatter, ColoredFormatter
        ):
            return True
    return False


SUCCESS_LEVEL = 25
PROGRESS_LEVEL = 35
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")
logging.addLevelName(PROGRESS_LEVEL, "PROGRESS")


class SuccessLogger(logging.Logger):
    """带 success 方法的 Logger 类型，用于补全提示。"""

    def success(self, message, *args, **kwargs) -> None:
        if self.isEnabledFor(SUCCESS_LEVEL):
            self._log(SUCCESS_LEVEL, message, args, **kwargs)

    def progress(self, message, *args, **kwargs) -> None:
        if self.isEnabledFor(PROGRESS_LEVEL):
            self._log(PROGRESS_LEVEL, message, args, **kwargs)


_LEVEL_NAME_MAP = {
    "DEBUG": logging.DEBUG,  # 10
    "INFO": logging.INFO,  # 20
    "PROGRESS": PROGRESS_LEVEL,  # 蓝色 23
    "SUCCESS": SUCCESS_LEVEL,  # 25
    "WARNING": logging.WARNING,  # 30
    "WARN": logging.WARNING,  # 30
    "ERROR": logging.ERROR,  # 40
    "CRITICAL": logging.CRITICAL,  # 50
    "FATAL": logging.CRITICAL,  # 50
}


def _logger_success(self: logging.Logger, message, *args, **kwargs) -> None:
    """记录 SUCCESS 等级日志。"""
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


def _logger_progress(self: logging.Logger, message, *args, **kwargs) -> None:
    """记录 PROGRESS 等级日志。"""
    if self.isEnabledFor(PROGRESS_LEVEL):
        self._log(PROGRESS_LEVEL, message, args, **kwargs)


if not hasattr(logging.Logger, "success"):
    setattr(logging.Logger, "success", _logger_success)

if not hasattr(logging.Logger, "progress"):
    setattr(logging.Logger, "progress", _logger_progress)


def _normalize_level(level: Union[int, str]) -> int:
    """
    规范化日志等级。

    支持传入 int 或字符串（大小写不敏感），如 "debug"、"INFO"。
    """
    if isinstance(level, str):
        text = level.strip()
        if text.isdigit():
            return int(text)

        key = text.upper()
        if key in _LEVEL_NAME_MAP:
            return _LEVEL_NAME_MAP[key]
        raise ValueError(
            f"不支持的日志等级: {level!r}。支持: DEBUG/INFO/PROGRESS/SUCCESS/WARNING/WARN/ERROR/CRITICAL/FATAL"
        )
    return int(level)


def setup_logger(
    name: Optional[str] = None,
    level: Union[int, str] = logging.DEBUG,
    stream: Optional[TextIO] = None,
    message_only: bool = False,
) -> SuccessLogger:
    """
    创建并配置彩色日志输出。

    Args:
        name: logger 的名称，默认 全局共享1个 logger 实例。
            示例：
            # 在 network.py
            logger_a = setup_logger("network")
            logger_a.debug("网络调试信息")

            # 在 db.py
            logger_b = setup_logger("db")
            logger_b.debug("数据库调试信息")
        作用:
            通过不同名称创建的 logger 互不干扰，适合在大型项目中使用。
                            每个 logger 设置不同的日志级别、格式、输出流等。
                level: 日志等级。支持 int 或字符串，默认 "DEBUG"。根据等级过滤后交给 handler 输出。
                    常用等级：DEBUG(10), INFO(20), SUCCESS(25), WARNING(30), PROGRESS(35), ERROR(40), CRITICAL(50)。
                    字符串支持："DEBUG"、"INFO"、"PROGRESS"、"SUCCESS"、"WARNING"/"WARN"、"ERROR"、"CRITICAL"/"FATAL"（大小写不敏感）。
            stream: 输出流，默认 sys.stdout。
            message_only: 是否仅输出日志消息（不包含时间与等级），默认 False。

    Returns:
        配置完成的 logger。示例:
            logger = setup_logger()
            logger.debug("这是一条调试信息")      # 青色
            logger.info("这是一条普通信息")       # 白色/默认
            logger.success("这是一条成功信息")    # 绿色
            logger.progress("这是一条进度信息")   # 蓝色
            logger.warning("这是一条警告信息")    # 黄色
            logger.error("这是一条错误信息")      # 红色
            logger.critical("这是一条严重错误信息")  # 紫色
    """

    logger = cast(SuccessLogger, logging.getLogger(name))
    normalized_level = _normalize_level(level)
    logger.setLevel(normalized_level)

    # 已配置彩色 handler 时直接复用，避免重复添加导致日志重复输出
    if _has_colored_handler(logger):
        return logger

    actual_stream = stream or sys.stdout
    console_handler = logging.StreamHandler(actual_stream)
    console_handler.setLevel(normalized_level)
    if message_only:
        formatter = ColoredFormatter("%(message)s", stream=actual_stream)
    else:
        formatter = ColoredFormatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            stream=actual_stream,
        )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
