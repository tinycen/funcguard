# 日志工具

FuncGuard 基于标准库 `logging` 提供彩色日志输出，封装在 `funcguard/log_utils.py`。
核心入口是 `setup_logger`，支持格式预设、固定时区、终端颜色感知。

## setup_logger - 创建彩色 logger

```python
from funcguard import setup_logger

# 基本使用（命名 logger，推荐）
logger = setup_logger("myapp")
logger.info("这是一条普通信息")

# 仅输出消息（不含时间与等级）
logger = setup_logger("myapp", format="message")

# 时间 + 消息，固定北京时间（适用于非北京时区的机器/容器）
logger = setup_logger("myapp", format="time_message", tz="bj")

# 跨午夜任务或日志归档：显示完整日期
logger = setup_logger("myapp", datefmt="%Y-%m-%d %H:%M:%S")

# 高级需求：直接传 logging 原始格式模板
logger = setup_logger("myapp", format="%(levelname)s %(message)s")
```

**参数说明：**

- `name`: logger 名称，不同名称的 logger 互不干扰。不传时拿到的是 root logger，
  在其上挂 handler 会影响进程内所有库的 logging 输出，**建议传入命名 logger**
- `level`: 日志等级，支持 int 或字符串（大小写不敏感），默认 `"DEBUG"`。
  支持 `DEBUG`/`INFO`/`PROGRESS`/`SUCCESS`/`WARNING`/`WARN`/`ERROR`/`CRITICAL`/`FATAL`
- `stream`: 输出流，默认 `sys.stdout`（emit 时动态解析，`redirect_stdout` /
  pytest `capsys` 可正常捕获）；显式传入时（如文件对象）尊重绑定
- `format`: 输出格式，支持预设名或原始模板，默认 `None`（等价于 `"full"`）：

  | 预设名 | 对应模板 | 输出示例 |
  |--------|----------|----------|
  | `"full"` | `%(asctime)s - %(levelname)s - %(message)s` | `10:00:00 - INFO - 消息` |
  | `"time_message"` | `%(asctime)s %(message)s` | `10:00:00 消息` |
  | `"message"` | `%(message)s` | `消息` |

  预设名以外的字符串按 logging 原始模板处理（如 `"%(levelname)s %(message)s"`）。
  预设名不含 `%`、模板必含 `%`，两者共用一个参数、永不混淆。

- `datefmt`: 时间格式，默认 `"%H:%M:%S"`（时分秒）。跨午夜任务、日志归档等
  需要完整日期时传 `"%Y-%m-%d %H:%M:%S"`
- `tz`: 时间戳时区，默认 `"local"`（本地时区）。支持 `"local"`/`"utc"`/`"bj"`/`"jp"`，
  与 `get_now` 的 `from_timezone` 风格统一。非北京时间机器上需要固定北京时间时传 `"bj"`

**返回值：** 配置完成的 logger（`logging.Logger` 子类，附带 `success`/`progress` 方法）

---

## 自定义日志等级

在标准等级基础上扩展了两个等级：

| 等级 | 数值 | 颜色 | 调用方式 |
|------|------|------|----------|
| `SUCCESS` | 25 | 绿色 | `logger.success("...")` |
| `PROGRESS` | 35 | 蓝色 | `logger.progress("...")` |

完整颜色对照：DEBUG 青色、INFO 白色、SUCCESS 绿色、WARNING 黄色、
PROGRESS 蓝色、ERROR 红色、CRITICAL 紫色。

---

## 颜色行为（终端感知）

- ANSI 颜色码**仅在真实终端（tty）输出**；管道、文件、CI 等非终端环境自动
  降级为纯文本，subprocess 捕获无需清洗
- 环境变量开关：`NO_COLOR=1` 强制禁用颜色（[no-color.org](https://no-color.org) 标准），
  `FORCE_COLOR=1` 强制启用颜色（优先级高于 tty 检测）
- 旧版 Windows CMD 不支持 ANSI 颜色码，可能显示为乱码，请升级终端

---

## 设计细节

- **防重复输出**：同名 logger 重复调用 `setup_logger` 时复用已有 handler；
  且 `propagate=False`，用户调用 `logging.basicConfig()` 后不会双份输出
- **stream 动态解析**：默认 handler 在每次 emit 时取当前 `sys.stdout`，
  因此 `import` 后再做 `redirect_stdout` / `capsys` 捕获仍然有效
- **时区实现**：通过 `Formatter.converter` 标准扩展点替换时间转换函数，
  不影响 logging 的其他行为

---

## 与 time_log 配合（logger 注入）

`time_log` 支持 `logger` 参数，传入后由其统一接管输出（时间格式与时区由
该 logger 决定，`time_log` 不再叠加时间戳）：

```python
from funcguard import time_log, setup_logger

my_logger = setup_logger("myapp", format="time_message", tz="bj")
time_log("开始处理", level="INFO", logger=my_logger)
```

注意：

- 请传入**命名 logger**，不要传 root logger
- 若 logger 格式为 `format="message"`（不含时间），输出将不带时间戳；
  需要时间请配 `format="time_message"` + `tz="bj"`，或直接使用 `time_log`
  默认的内置 logger（北京时间、`HH:MM:SS 消息` 格式）

---

## 从旧版迁移

- `setup_logger(message_only=True)` → `setup_logger(format="message")`
- `setup_logger(message_only=False)` → 默认行为（`format="full"`），无需传参
- 默认时间格式从 `%Y-%m-%d %H:%M:%S` 变为 `%H:%M:%S`；需要完整日期时
  显式传 `datefmt="%Y-%m-%d %H:%M:%S"`
- `time_log` 的 `level` 参数为空时，行为从 `print` 输出变为按 `INFO` 级别
  走 logger 输出（非终端环境下输出内容不变，仍为 `HH:MM:SS 消息` 纯文本）
