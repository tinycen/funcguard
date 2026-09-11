"""Logging utilities for funcguard."""

import logging
import os
import sys
from datetime import datetime, timedelta, timezone
from typing import TextIO, cast


def _color_enabled() -> bool:
    """
    判断当前是否启用 ANSI 颜色输出。

    优先级：NO_COLOR（禁用） > FORCE_COLOR（启用） > sys.stdout.isatty()。
    非终端环境（管道/文件/CI）自动输出纯文本。
    """
    if os.environ.get("NO_COLOR"):  # https://no-color.org
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return bool(getattr(sys.stdout, "isatty", None) and sys.stdout.isatty())


class ColoredFormatter(logging.Formatter):
    """彩色日志格式化器。仅在真实终端输出颜色，管道/文件场景自动降级为纯文本。"""

    # 注意：Windows 自带的终端（尤其老版本 CMD）不原生支持 ANSI 颜色码，
    # 直接输出 \033[31m 等控制字符可能会显示成乱码，请升级终端。

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

    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if not _color_enabled():
            return message
        color = self.COLORS.get(record.levelname, self.COLORS["INFO"])
        return f"{color}{message}{self.COLORS['RESET']}"


# 格式预设：预设名不含 '%'，原始模板必含 '%'，两者共用一个 format 参数、永不混淆
_FORMAT_PRESETS = {
    "message": "%(message)s",
    "time_message": "%(asctime)s %(message)s",
    "full": "%(asctime)s - %(levelname)s - %(message)s",
}

# 固定时区映射（与 get_now 的 from_timezone 风格统一）
_TZ_MAP = {
    "utc": timezone.utc,
    "bj": timezone(timedelta(hours=8)),
    "jp": timezone(timedelta(hours=9)),
}


class _LazyStdoutHandler(logging.StreamHandler):
    """emit 时动态取 sys.stdout，避免 import 期绑定导致 redirect_stdout/capsys 失效。"""

    def __init__(self, level: int = logging.NOTSET):
        logging.Handler.__init__(self, level)  # 跳过 StreamHandler 的 stream 绑定

    @property
    def stream(self):
        return sys.stdout

    @stream.setter
    def stream(self, value):  # 吃掉 StreamHandler.__init__ 路径的赋值
        pass


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


def _normalize_level(level: int | str) -> int:
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
    name: str | None = None,
    level: int | str = logging.DEBUG,
    stream: TextIO | None = None,
    format: str | None = None,
    datefmt: str = "%H:%M:%S",
    tz: str = "local",
) -> SuccessLogger:
    """
    创建并配置彩色日志输出。

    Args:
        name: logger 的名称，默认全局共享1个 logger 实例。
            示例：
                # 在 network.py
                logger_a = setup_logger("network")
                logger_a.debug("网络调试信息")

                # 在 db.py
                logger_b = setup_logger("db")
                logger_b.debug("数据库调试信息")

            作用：通过不同名称创建的 logger 互不干扰，适合在大型项目中使用。
            每个 logger 设置不同的日志级别、格式、输出流等。
            注意：不传 name 时拿到的是 root logger，在其上挂 handler 会影响
            进程内所有库的 logging 输出，建议传入命名 logger。
        level: 日志等级。支持 int 或字符串，默认 "DEBUG"。根据等级过滤后交给 handler 输出。
            常用等级：DEBUG(10), INFO(20), SUCCESS(25), WARNING(30), PROGRESS(35), ERROR(40), CRITICAL(50)。
            字符串支持："DEBUG"、"INFO"、"PROGRESS"、"SUCCESS"、"WARNING"/"WARN"、"ERROR"、"CRITICAL"/"FATAL"（大小写不敏感）。
        stream: 输出流，默认 sys.stdout（emit 时动态解析，redirect_stdout/capsys 可正常捕获）。
            显式传入时（如文件对象）尊重绑定。
        format: 输出格式。支持预设名或原始模板，默认 None（等价于 "full"）。
            预设名：
                "full":         "%(asctime)s - %(levelname)s - %(message)s"（完整格式）
                "time_message": "%(asctime)s %(message)s"（时间 + 消息）
                "message":      "%(message)s"（仅消息）
            原始模板：直接传 logging 格式串，如 "%(levelname)s %(message)s"。
        datefmt: 时间格式，默认 "%H:%M:%S"（时分秒）。跨午夜任务或日志归档场景
            可传 "%Y-%m-%d %H:%M:%S" 显示完整日期。
        tz: 时间戳时区，默认 "local"（本地时区）。支持 "local"/"utc"/"bj"/"jp"，
            与 get_now 的 from_timezone 风格统一；非北京时间机器上需要固定
            北京时间时传 "bj"。

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
    # 关闭传播，避免用户调用 logging.basicConfig() 后同一条日志双份输出
    logger.propagate = False

    # 已配置彩色 handler 时直接复用，避免重复添加导致日志重复输出
    if _has_colored_handler(logger):
        return logger

    # 显式指定 stream 时尊重绑定；默认动态解析 sys.stdout
    if stream is not None:
        console_handler: logging.StreamHandler = logging.StreamHandler(stream)
    else:
        console_handler = _LazyStdoutHandler()
    console_handler.setLevel(normalized_level)

    # 预设名命中则映射为模板，否则按原始模板使用；空值回落到完整格式
    fmt = _FORMAT_PRESETS.get(format, format) if format else None
    if fmt is None:
        fmt = _FORMAT_PRESETS["full"]
    formatter = ColoredFormatter(fmt, datefmt=datefmt)

    # 固定时区：通过 Formatter.converter 标准扩展点替换时间转换函数
    if tz != "local":
        if tz not in _TZ_MAP:
            raise ValueError(f"不支持的时区: {tz!r}。支持: local/utc/bj/jp")
        tzinfo = _TZ_MAP[tz]
        formatter.converter = lambda ts: datetime.fromtimestamp(ts, tzinfo).timetuple()

    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger
