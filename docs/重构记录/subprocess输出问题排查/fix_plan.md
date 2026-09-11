# subprocess 输出丢失：问题判定与修复方案

> **状态：已于 0.3.0 实施完成（破坏性更新）。**
> 实施范围：P0~P4 全部落地（`funcguard/log_utils.py`、`funcguard/time_utils.py`、
> `funcguard/printer.py`），测试 `tests/test_print_progress.py` 已按新行为重写
> （14 用例全过）。0.3.0 的破坏性变更：
> `setup_logger` 删除 `message_only` 参数（迁移：`format="message"`）、
> 默认时间格式从完整日期变为 `%H:%M:%S`、`time_log` 空 level 从 print 改为
> INFO 级 logger 输出、`print_progress` 非 tty 下降级为步进换行输出。
> 当前行为文档：[printer.md](../../printer.md)、[logger.md](../../logger.md)、
> [subprocess_output.md](../../subprocess_output.md)。

本文对同目录两篇排查文档（[print_progress](./print_progress_subprocess.md)、
[time_log](./time_log_subprocess.md)）中描述的缺陷逐条对照源码做存在性判定，
并核对"输出丢失是 stdio 缓冲机制所致"这一推断，最后给出修复方案。

> 判定依据：funcguard 源码（`funcguard/printer.py`、`funcguard/time_utils.py`、
> `funcguard/log_utils.py`）逐行核对 + 4 组对照实验（E1~E4，Windows 11 / Python 3.13）。

---

## 一、判定结论速览

| # | 问题 | 判定 | 证据 |
|---|------|------|------|
| 1 | `print_progress` 中 `idx > total` 时进度条溢出 | **存在** | `printer.py:21-24`，`percent` 无钳制，`150//2=75` 超出设计宽度 50 |
| 2 | `\r` 只覆盖不清行，残留上一帧字符 | **存在** | `printer.py:30`，仅 `\r` 无 `\033[K` 或空格回填 |
| 3 | `print_progress` 不感知非 tty 环境 | **存在** | `printer.py` 全文无 `isatty()` 判断 |
| 4 | `ColoredFormatter` 无条件注入 ANSI 颜色码 | **存在** | `log_utils.py:25-28`，`format()` 无 `isatty()`/`NO_COLOR` 判断 |
| 5 | logger 的 stream 在 import 时绑定死 | **存在** | `time_utils.py:10` 模块级建 logger + `log_utils.py:163` `StreamHandler(stream or sys.stdout)` |
| 6 | 编码失败时 logger 静默吞掉日志（`rc=0`） | **存在** | Python `logging` 模块天性：`emit()` 捕获异常只印 `--- Logging error ---`，不重抛 |
| 7 | `propagate` 未关闭，`basicConfig` 后双份输出 | **存在** | `log_utils.py` 的 `setup_logger` 未设 `logger.propagate = False` |
| 8 | `time_wait` 与 `print_progress` 同样的 `\r` 问题 | **存在** | `time_utils.py:304-308` |
| 9 | **库内多个 print 路径无 `flush=True`** | **存在（文档未覆盖，新发现）** | `time_utils.py:38, 72`（`time_log` 的 print 分支）、`time_utils.py:112-126`（`time_diff`）、`printer.py:43, 55, 71-74`（`print_title`/`print_line`/`print_block`） |

9 条全部属实，修复方案见第三、四节。

---

## 二、对"缓冲机制导致输出丢失"推断的核对

推断原文要点：丢失的主因是 stdio 缓冲（管道下块缓冲、异常退出时缓冲区丢弃），
不是 print/logger 混用；`\r` 进度条 + 按行读取是"部分信息没捕获到"的元凶。

### 2.1 缓冲机制是丢失的主因 —— **正确（实验证实）**

E1：子进程 `print("buffered-line")`（无 flush）后死循环，1.2s 后被 `kill()`：

| 子进程启动方式 | kill 后父进程捕获 |
|----------------|-------------------|
| 默认（管道下 stdout 块缓冲） | `b''` —— **整条丢失** |
| `PYTHONUNBUFFERED=1` | `b'buffered-line\r\n'` —— 完整保留 |

结论成立。补充两点精确化：

- **logger 路径反而天然免疫**。`logging.StreamHandler.emit()` 每次都会 `self.flush()`，
  走 `color_logger` 的日志不经过用户态缓冲。真正会因缓冲丢失的是 **无 flush 的
  print 路径**（第 9 条列出的那些），这也是 funcguard 侧最需要补的地方。
- **stderr 不丢**。CPython ≥3.9 的 `sys.stderr` 永远 unbuffered，traceback 本身
  一定能到达管道。所谓"看不到完整报错链条"，丢的通常是报错**之前** print 的
  上下文信息，而不是 traceback 本身。

### 2.2 "`\r` 进度条是元凶" —— **方向对，但需要修正**

`print_progress` **已经带 `flush=True`**（`printer.py:30`），它的每一帧在写入瞬间
就已进入管道内核缓冲区，即使子进程随后被 kill，这些帧也不会丢。文档一的流式
实验（帧跨度 ≈1.6s）也证实了 flush 生效。

`\r` 的真正危害不是"丢失"，而是**按行读取时的实时性灾难**：

E3（二进制模式 `readline()`）：子进程写 `F1\r` 并 flush，sleep 2s 后再写 `F2\n`：

```
readline() 等待 2.1s（直到 \n 出现），一次返回 b'F1\rF2\r\n'
```

二进制 `readline()` 只认 `\n`，`\r` 分隔的帧全部积压在父进程一侧，直到出现
`\n` 或 EOF 才一次性放行 —— 看起来像"卡住/丢了"，实际数据在，只是读不到。

E4（text 模式 `readline()`，同样的子进程）：

```
readline() 同样等待 2.1s，返回 'F1\n'
```

即使 text 模式把 `\r` 视为行边界，`TextIOWrapper` 收到行尾的 `\r` 时无法立即
区分它是 `\r` 还是 `\r\n` 的前半，**必须等下一帧的首字节到达才能确认**，于是
每一帧都延迟一帧；最后一帧则会卡到 EOF。这就是"进度条部分信息长时间看不到"
的完整机制：**子进程没丢，父进程读法不对。**

### 2.3 "确认 StreamHandler 是否缓存了 sys.stdout" —— **预判准确**

funcguard 恰恰就是缓存的那类库（`log_utils.py:163`，import 期绑定）。但要明确
影响边界：

| 场景 | 是否受影响 |
|------|-----------|
| 同进程 `redirect_stdout` / pytest `capsys` | **受影响**，logger 输出漏到真实 stdout |
| subprocess 管道捕获 | **不受影响**。子进程 import 时 `sys.stdout` 已是管道，绑定的是正确对象 |

所以它不是 subprocess 丢失的原因，但值得顺手修（修复后 funcguard 才可被
常规测试手段捕获）。

### 2.4 推断中给出的对策 —— **全部采纳**

`PYTHONUNBUFFERED=1`、合并 stderr、非行读取、`isatty()` 降级、print 补
`flush=True`，均与实验结论一致，分别落在第三、四节。

---

## 三、funcguard 侧修复（按优先级）

所有改动互不依赖，可逐个落地、逐个发布。

### P0：`time_log` 消灭 print 路径（单 logger 化 + logger 注入 + 时间戳收口）

`time_log` 目前是双路径：`level` 非空走 `color_logger`，为空走 `print`
（`time_utils.py:35-38` 与 `69-72`）。两条路径在四个维度上行为全部不一致：

| 维度 | print 分支 | logger 分支 |
|------|-----------|-------------|
| 缓冲 | 管道下块缓冲，异常退出时丢失（E1） | `emit()` 自带 flush，免疫 |
| 编码失败 | 抛 `UnicodeEncodeError`，`rc=1` | 静默吞掉，`rc=0` |
| 颜色 | 无 ANSI | 有 ANSI（修复 P3 后按 tty 感知） |
| 重定向捕获 | 动态 `sys.stdout`，可捕获 | import 期绑定（修复 P3 后可捕获） |

这是库内**唯一的真实重复逻辑**，修它的方式是合并路径，而不是合并模块
（进度条/标题等终端 UI 与 logging 的"每条 record 强制换行 + 等级过滤"模型
天然冲突，不应纳入 logger，保持 print 即可）。

改动分三步：

**1. 签名注入 logger 参数（`time_utils.py:14`）**

```python
import logging

def time_log(message, i=0, max_num=0, s_time=None, start_from=0,
             return_field="progress_info", level="",
             logger: logging.Logger | None = None):
```

调用方可传入自己的 logger（如 `setup_logger("myapp")` 的返回值）统一接管
输出的 handler、等级与格式；默认 `None` 时使用内置 `color_logger`，行为不变；
测试时可注入 mock logger。

**2. 两处输出分支合并（`time_utils.py:35-38` 与 `69-72`，同改）**

```python
_logger = logger or color_logger
if level:
    _logger.log( _normalize_level( level ), message )   # 第二处再拼上 progress_info
else:
    _logger.info( message )
```

`level` 为空时默认走 INFO，print 分支整体删除。

**3. 时间戳收口到 logger（依赖 P3 的时区/格式支持）**

内置 logger 改配（`time_utils.py:10`）：

```python
color_logger = setup_logger("funcguard_time_logger",
                            format="time_message", tz="bj")
```

`time_log` 内不再拼接 `time_str`（`now` 变量保留，仍参与 ETA 计算）。
`"time_message"` 预设 + 默认 `datefmt="%H:%M:%S"`，输出与现状**逐字符一致**
（"10:00:00 消息"），时区固定北京。传入自定义 logger 时，时间格式与时区
由该 logger 全权决定，`time_log` 不再叠加 —— 双时间戳问题彻底消失。

收益：

- **缓冲丢失面直接消失**：走 logger 后每次 `emit()` 自动 `flush()`，
  `time_log` 对 E1 场景（子进程被 kill）免疫，不再依赖调用方设
  `PYTHONUNBUFFERED=1`。
- 双路径的四重行为分裂（上表）归一，颜色管理统一收口到 `ColoredFormatter`。
- logger 注入使调用方可以统一管理输出目标与等级，测试可注入 mock。

行为变化与兼容性：

- 非 tty 下输出与原 print 路径**完全一致**（"HH:MM:SS 消息"、无 ANSI 残留，
  前提是 P3 的 tty 感知与时区支持已落地）。
- tty 下无 `level` 的输出带 INFO 颜色（白色），属改进而非破坏。
- 传入 `format="message"` 的 logger 时输出**没有时间**：docstring 需提醒，
  需要时间显示就配 `format="time_message"` + `tz="bj"`，
  或直接用默认 `color_logger`。
- 避免传入 root logger：`setup_logger()` 不传 name 时拿到的是
  `logging.getLogger(None)`（root），在其上挂 handler 会影响进程内所有库的
  logging 输出，docstring 需提醒传入命名 logger。
- 编码失败的表象从"print 抛异常 `rc=1`"变为"logger 静默吞 `rc=0`"：
  两者都不理想，靠 `PYTHONIOENCODING=utf-8` 从源头规避（见第四节），
  变化可接受。

### P1：其余 `print` 路径补 `flush=True`

`time_log` 的两处 print 随 P0 消失，剩余需补 flush 的位置：

| 位置 | 改动 |
|------|------|
| `time_utils.py:112-126`（`time_diff` 全部 print） | 各加 `flush=True` |
| `printer.py:43, 55, 71-74`（`print_title`/`print_line`/`print_block`） | 各加 `flush=True` |

管道下块缓冲 + 进程异常退出 = 缓冲区整条丢弃（E1 已证实）。补上 flush 后，
即使被 kill，已打印内容也全部在管道里。logger 路径（`emit` 自带 flush）无需改动。

### P2：`print_progress` 三处加固（`printer.py`）

```python
import sys

def print_progress(idx: int, total: int, message: str = "") -> None:
    if total <= 0:
        print(f"警告: total 必须大于 0（当前值: {total}）")
        return

    # 加固 1：钳制百分比，修复 idx > total 时条体溢出 50 字符
    percent = max(0, min(100, int(idx / total * 100)))
    bar = '█' * (percent // 2) + '-' * (50 - percent // 2)
    text = f"进度: |{bar}| {percent}% ({idx}/{total}) {message}"

    if sys.stdout.isatty():
        # 终端：\r 原地覆盖；\033[K 清行尾，修复 message 变短时的残留
        print(f"\r\033[K{text}", end='', flush=True)
    else:
        # 非终端（管道/文件/CI）：降级为步进换行输出，避免 \r 帧在管道里
        # 失去覆盖语义、并触发按行读取的延迟问题（E3/E4）
        last = getattr(print_progress, "_last_percent", -10)
        if percent == 100 or percent - last >= 10:
            print(text, flush=True)
            print_progress._last_percent = percent
```

要点：

- `\033[K`（清行尾）只在 tty 分支发送，不污染管道日志。
- 非 tty 分支按 10% 步进 + 100% 必打，CI 日志不会被刷爆；`_last_percent`
  挂在函数对象上，不引入模块级状态。

### P2：`time_wait` 同步降级（`time_utils.py:304-308`）

```python
import sys

def time_wait(seconds: int = 10):
    interactive = sys.stdout.isatty()
    for remaining in range(seconds, 0, -1):
        if interactive:
            print(f"\r\033[KTime wait: {remaining}s ", end="", flush=True)
        else:
            print(f"Time wait: {remaining}s", flush=True)
        time.sleep(1)
    if interactive:
        print()
```

### P3：`ColoredFormatter` 感知终端（`log_utils.py`）

```python
import os

def _color_enabled() -> bool:
    if os.environ.get("NO_COLOR"):      # https://no-color.org
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    stream = sys.stdout
    return bool(getattr(stream, "isatty", None) and stream.isatty())

class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if not _color_enabled():
            return message
        color = self.COLORS.get(record.levelname, self.COLORS["INFO"])
        return f"{color}{message}{self.COLORS['RESET']}"
```

每次 `format` 动态判断（而不是在 handler 初始化时定死），兼顾运行时重定向。
修复后管道捕获自动得到干净文本，终端里颜色不变；`NO_COLOR`/`FORCE_COLOR`
两个事实标准环境变量作为显式开关。

### P3：`setup_logger` 支持格式预设与时区（`log_utils.py`）

**格式：`format` 预设名 + 原始模板混合（取代 `message_only`）**

预设名不含 `%`、模板必含 `%`，两者共用一个参数、永不混淆：

```python
_FORMAT_PRESETS = {
    "message":      "%(message)s",
    "time_message": "%(asctime)s %(message)s",
    "full":         "%(asctime)s - %(levelname)s - %(message)s",
}

def setup_logger(name=None, level=logging.DEBUG, stream=None,
                 format: str | None = None,
                 datefmt: str = "%H:%M:%S",
                 tz: str = "local"):
    ...
    fmt = _FORMAT_PRESETS.get(format, format)  # 命中预设则映射，否则当原始模板
    if fmt is None:
        fmt = _FORMAT_PRESETS["full"]
    formatter = ColoredFormatter(fmt, datefmt=datefmt)
```

要点：

- `format` 与 `datefmt` 成对设计，与 `logging.basicConfig(format=..., datefmt=...)`
  完全同构，会用标准库的人零迁移成本。
- `format=None` → `"full"`（原 `message_only=False` 的行为）；
  `format="message"` 等价于原 `message_only=True`；长尾需求直接传原始模板
  （如 `"%(levelname)s %(message)s"`），不受预设表限制。
- **`datefmt` 默认从 logging 的完整日期改为 `"%H:%M:%S"`**：日常跑批只需
  时分秒；跨午夜任务、日志归档等场景才显式传
  `datefmt="%Y-%m-%d %H:%M:%S"`。默认输出格式因此变化，CHANGELOG 需注明。
- **`message_only` 参数直接删除**：迁移写法 `message_only=True` →
  `format="message"`；内部唯一使用点 `time_utils.py:10` 由 P0 顺手迁移，
  同版本发布，CHANGELOG 注明。

**时区：`tz` 参数（`Formatter.converter` 标准扩展点）**

logging 的时间戳由 `Formatter.formatTime()` 生成，默认走 `time.localtime()`
（**本地时区**，在非北京时间的机器/容器上会偏差）。其公开扩展点
`Formatter.converter` 可整体替换时间转换函数（官方文档认可，例如
`formatter.converter = time.gmtime` 即切 UTC），利用它支持固定时区：

```python
from datetime import datetime, timezone, timedelta

_TZ_MAP = {
    "utc": timezone.utc,
    "bj":  timezone(timedelta(hours=8)),
    "jp":  timezone(timedelta(hours=9)),
}

# setup_logger 内，formatter 创建之后：
if tz != "local":
    tzinfo = _TZ_MAP[tz]
    formatter.converter = lambda ts: datetime.fromtimestamp(ts, tzinfo).timetuple()
```

要点：

- `tz` 取值 `"local"/"utc"/"bj"/"jp"`，与 `get_now` 的 `from_timezone`
  风格统一；默认 `"local"` 时行为与现状完全一致（向后兼容）。
- P0 第 3 步依赖本节的 `format`/`tz`，把 `time_log` 的时间戳收口进
  logger（北京时区 + 时分秒），从而消除传入 logger 时的双时间戳问题。

### P3：stream 动态解析（`log_utils.py`）

```python
class _LazyStdoutHandler(logging.StreamHandler):
    """emit 时动态取 sys.stdout，避免 import 期绑定导致重定向失效。"""

    def __init__(self, level: int = logging.NOTSET):
        logging.Handler.__init__(self, level)  # 跳过 StreamHandler 的绑定

    @property
    def stream(self):
        return sys.stdout

    @stream.setter
    def stream(self, value):  # 吃掉 StreamHandler.__init__ 路径的赋值
        pass
```

`setup_logger` 中按需选用：

```python
if stream is not None:
    console_handler = logging.StreamHandler(stream)   # 显式指定，尊重绑定
else:
    console_handler = _LazyStdoutHandler()            # 默认动态解析
```

同时把 `_has_colored_handler` 的 `isinstance(handler, logging.StreamHandler)`
检查保留即可（`_LazyStdoutHandler` 是其子类，去重逻辑不受影响）。

### P4：关闭传播（`log_utils.py` 的 `setup_logger`）

```python
logger.propagate = False
```

消除用户调用 `logging.basicConfig()` 后 stdout/stderr 双份输出的问题。

---

## 四、调用侧修复（不改库即可消除大部分丢失）

```python
import os, subprocess, sys

env = dict(os.environ,
           PYTHONUNBUFFERED="1",        # 子进程 stdout/stderr 不缓冲
           PYTHONIOENCODING="utf-8")    # 两端编码钉死，防 GBK/cp1252 静默吞日志

proc = subprocess.Popen(
    [sys.executable, "worker.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,           # 合并 stderr，报错链条与上下文同序
    bufsize=0,                          # unbuffered raw：read 按块立即返回
    env=env,
)
while chunk := proc.stdout.read(4096):  # 按块读而非按行读，兼容 \r 帧（E3/E4）
    sys.stdout.buffer.write(chunk)
    sys.stdout.buffer.flush()
rc = proc.wait()
```

四条措施的对应关系：

| 措施 | 消除的问题 |
|------|-----------|
| `PYTHONUNBUFFERED=1` | 子进程被 kill 时用户态缓冲区整条丢弃（E1） |
| `stderr=STDOUT` | traceback 与 print 上下文分离在两个管道、时序错乱 |
| `bufsize=0` + 按块 `read(4096)` | 二进制 `readline` 阻塞（E3）、text `readline` 因 `\r\n` 歧义延迟一帧（E4） |
| `PYTHONIOENCODING=utf-8` | 编码不匹配 → logger 静默吞日志 / 父进程解码线程炸导致 `stdout=None` |

注意 `bufsize=0` 时 `proc.stdout` 是 unbuffered 的 `FileIO`，`read(4096)` 对应
一次系统 read，**有数据即返回**，不会等满 4096；若保留默认缓冲，`read(n)` 会
试图读满 n 字节才返回，实时性同样差。拿到的是原始字节，`\r` 语义完整保留，
需要文本时 `chunk.decode("utf-8", errors="replace")`。

---

## 五、不属于 bug、无需修复的行为

- `text=True` 把 `\r` 规范化为 `\n`（11 帧变 12 行）：universal newlines 标准
  行为，文档一已记录；需要原始帧就走二进制捕获。
- logger 编码失败只印 `--- Logging error ---` 不重抛：logging 模块设计如此，
  funcguard 侧无法也无必要改变；靠 `PYTHONIOENCODING=utf-8` 从源头规避。
- subprocess 场景下 import 期绑定 stream：子进程 import 时 `sys.stdout` 已是
  正确管道，无实际影响；P3 的 lazy handler 是为同进程重定向/测试场景而修。

## 六、验收要点

修复落地后，用以下最小场景验证（均来自本文实验，可直接复现）：

1. 无 flush print + kill → 修复后应捕获到已打印内容（E1 场景）。
2. `print_progress(15, 10)` → 条体仍 50 字符，显示 100%。
3. 管道捕获 `print_progress` 全循环 → 行数 ≈ 11 行（步进输出）而非按帧堆积。
4. 管道捕获 `time_log(..., level="ERROR")` → stdout 无 `\x1b` 残留。
5. `redirect_stdout` + `time_log(..., level="INFO")` → 能被 buf 捕获。
6. `logging.basicConfig()` 后再用 `color_logger` → 单份输出。
7. `time_log("msg")`（不带 level）→ 走 logger 单路径输出；管道捕获下与原
   print 路径等价（"HH:MM:SS 消息"、无 ANSI），且子进程被 kill 时不丢失（E1 场景）。
8. `time_log("msg", level="INFO", logger=setup_logger("myapp",
   format="time_message", tz="bj"))` → 输出单时间戳（无重复），且在
   非北京时区的机器上仍显示北京时间（时分秒格式）。
9. `setup_logger("app")` 默认输出 → `"10:00:00 - INFO - 消息"`（时分秒）；
   `setup_logger("app", format="message")` → `"消息"`（原 message_only=True 等价）。
