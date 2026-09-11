# time_log 彩色日志在 subprocess 中的输出与捕获

本文分析 `funcguard/time_utils.py` 的日志打印功能在 `subprocess` 场景下的表现：
颜色编码会不会造成乱码、捕获到的到底是什么、以及由此牵出的几个静默失败陷阱。

> 排查环境：Windows 11 / Python 3.13.14 / funcguard 工作区
> 相关文档：[print_progress 在 subprocess 中的打印行为与测试](./print_progress_subprocess.md)

---

## 结论速览

| 问题 | 结论 |
|------|------|
| 捕获到的会是"乱码"吗？ | **不是乱码**，是 ANSI 控制字符 `\x1b[31m ... \x1b[0m` 原样残留 |
| 颜色码会无条件输出吗？ | **会**。`ColoredFormatter` 不判断 `isatty()`，管道里照样注入 |
| 会不会导致编码错误？ | 颜色码本身不会（ESC 在任何编码下都可表示）；**中文内容 + 编码不匹配才会** |
| 最危险的是什么？ | 编码失败时 logger 会**静默吞掉异常**，进程仍返回 `rc=0`，日志整条丢失 |
| `redirect_stdout` / `capsys` 能捕获吗？ | **不能**。logger 的 stream 在 import 时就被绑定死了 |

---

## 一、两条输出路径，行为完全不同

`time_log` 内部有分支（`time_utils.py:35-38` 与 `69-72`）：

```python
if level:
    color_logger.log(_normalize_level(level), time_str + " " + message)
else:
    print(time_str + " " + message)
```

| 维度 | `level` 为空 → `print()` | `level` 非空 → `color_logger` |
|------|--------------------------|-------------------------------|
| 颜色码 | 无 | 有（ANSI） |
| 输出流解析 | 每次动态取 `sys.stdout` | **import 时绑定，之后不变** |
| 编码失败 | 硬抛 `UnicodeEncodeError`，`rc=1` | **静默吞掉**，`rc=0`，stdout 为空 |
| 可被 `redirect_stdout` 捕获 | 是 | **否** |

---

## 二、颜色码：是残留，不是乱码

`log_utils.py:14-28` 的调色板：

```python
COLORS = {
    "DEBUG": "\033[36m", "INFO": "\033[37m", "PROGRESS": "\033[34m",
    "SUCCESS": "\033[32m", "WARNING": "\033[33m", "ERROR": "\033[31m",
    "CRITICAL": "\033[35m", "RESET": "\033[0m",
}
```

`ColoredFormatter.format()` 无条件包裹，**没有任何 `isatty()` / `NO_COLOR` 判断**。

### 实测：subprocess 捕获到的真实内容

```python
r = subprocess.run([...], capture_output=True, text=True, encoding="utf-8")
for line in r.stdout.splitlines():
    print(repr(line))
```

```
'\x1b[37m02:18:20 带level-INFO\x1b[0m'
'\x1b[32m02:18:20 带level-SUCCESS\x1b[0m'
'\x1b[31m02:18:20 带level-ERROR\x1b[0m'
'02:18:20 不带level-纯print'
```

**文字内容完整无损，不是 mojibake。** 多出来的 6 个 `\x1b` 是 ESC 控制字符。

### 这算乱码吗？分场景

| 消费方 | 表现 | 是否算"乱码" |
|--------|------|--------------|
| 现代终端（支持 ANSI） | 正常彩色 | 否 |
| 老版 `cmd.exe`（无 VT 支持） | 显示成 `←[31m` | 视觉上是 |
| 日志文件 / 数据库 | 存进 `\x1b[31m` 字面量 | 是（污染） |
| GitHub Actions / CI 日志 | 部分平台能渲染，部分显示原始码 | 视平台 |
| **字符串断言** | `"02:18:20 处理中" in stdout` 可能命中 | 但 `==` 断言必挂 |

**关键**：这是"控制字符污染"，不是"编码错误"。两者的成因和解法完全不一样 ——
前者靠正则清洗，后者靠统一编码。

---

## 三、陷阱一：logger 的 stream 在 import 时就被绑定

`time_utils.py:10` 是模块级代码：

```python
color_logger = setup_logger("funcguard_time_logger", message_only=True)
```

而 `setup_logger` 里（`log_utils.py:163`）：

```python
console_handler = logging.StreamHandler(stream or sys.stdout)
```

`StreamHandler.__init__` 会**立刻**把当前 `sys.stdout` 对象的引用存进 `self.stream`。
由于 `funcguard/__init__.py` 会 import `time_utils`，这个绑定发生在用户 `import funcguard` 的那一刻。

**后果：之后所有的 stdout 重定向对 logger 完全无效。**

### 实测

```python
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    time_log("A-带level走logger", level="INFO")
    time_log("B-不带level走print")
print(repr(buf.getvalue()))
```

```
redirect_stdout 捕获到的 -> '02:18:34 B-不带level走print\n'
A(logger) 被捕获 -> False
B(print)  被捕获 -> True
```

`A` 那条**漏到了真实 stdout**，一条都没进 `buf`。

影响面：
- `contextlib.redirect_stdout` 静默失效
- pytest 的 `capsys` / `capfd` 抓不到（若 funcguard 在测试采集阶段已被导入）
- 任何"运行时替换 sys.stdout"的日志接管方案都会漏掉这部分输出

---

## 四、陷阱二：编码失败会静默丢失日志（最危险）

Python `logging` 模块在 `emit()` 里捕获异常，只往 stderr 打印
`--- Logging error ---`，**不重新抛出**。

### 实测：中文内容 + `PYTHONIOENCODING=cp1252`

| 路径 | 返回码 | stdout | stderr |
|------|--------|--------|--------|
| logger（`level="ERROR"`） | **0** | `b''` | `--- Logging error --- ...` |
| print（不带 `level`） | **1** | `b''` | `UnicodeEncodeError: 'charmap' codec ...` |

同样是输出失败，行为天差地别：

- **print 路径**：进程崩了，`rc=1`，调用方立刻知道
- **logger 路径**：进程照常返回 `rc=0`，日志**整条消失**，调用方毫无察觉

对于"跑批任务 + 靠日志排查"的场景，这属于最难查的一类故障。

---

## 五、陷阱三：父进程解码失败时，`stdout` 会变成 `None`

如果子进程按 GBK 输出、父进程用 `encoding="utf-8"` 解码，
`UnicodeDecodeError` 发生在 `subprocess` 内部的 `_readerthread` 线程里，
**不会传播到主线程**。

### 实测

```python
r = subprocess.run([...], capture_output=True, text=True,
                   encoding="utf-8",
                   env=dict(os.environ, PYTHONIOENCODING="gbk"))
print(r.stdout)   # None
```

控制台只打印一段线程 traceback：

```
Exception in thread Thread-5 (_readerthread):
  ...
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xd6 in position 14: invalid continuation byte
```

`subprocess.run` **正常返回**，`r.stdout` 是 `None`。后续若做
`r.stdout.splitlines()`，会在离故障点很远的地方抛 `AttributeError`，极难定位。

### ANSI 在各种编码下的表现（对照）

| `PYTHONIOENCODING` | 返回码 | 结果 |
|---|---|---|
| `utf-8` | 0 | `b'\x1b[31m02:19:03 \xe4\xb8\xad...\x1b[0m'` 正常 |
| `gbk` | 0 | `b'\x1b[31m02:19:04 \xd6\xd0...\x1b[0m'` 正常（GBK 能编码中文） |
| `cp1252` | 0 | **stdout 空**，日志被吞 |

ESC（0x1B）在任何编码下都能表示，**颜色码本身从不引发编码错误**；
出问题的一定是中文正文。

---

## 六、陷阱四：`propagate=True` 导致重复输出

`setup_logger` 没有关闭传播。一旦用户调用过 `logging.basicConfig()`，
一条日志会同时走两条路：

### 实测

```
子进程 stdout: '\x1b[31m02:19:54 重复测试\x1b[0m'
子进程 stderr: 'ERROR:funcguard_time_logger:02:19:54 重复测试'
```

同一条消息，stdout 一份彩色、stderr 一份纯文本。**在 subprocess 里意味着
`stdout` 和 `stderr` 都拿到内容**，容易让上层误判为两条独立日志。

---

## 七、time_wait 同样有回车符问题

`time_utils.py:304-308`：

```python
for remaining in range(seconds, 0, -1):
    print(f"\rTime wait: {remaining}s ", end="", flush=True)
    time.sleep(1)
print()
```

和 `print_progress` 完全一样的 `\r` + `end=''` 模式，因此在 `text=True` 下同样被转换：

| 捕获方式 | `\r` | `\n` | 形态 |
|---------|------|------|------|
| `text=True` | 0 | 4 | `'\nTime wait: 3s \nTime wait: 2s \nTime wait: 1s \n'` |
| 二进制 | 4 | 1 | `'\rTime wait: 3s \rTime wait: 2s \rTime wait: 1s \r\n'` |

（`seconds=3` 时，3 个 `\r` + 结尾 `print()` 的 1 个 `\n`）

---

## 八、修复建议

以下改动互不依赖，可逐个落地。

### 1. 让颜色感知终端（推荐优先做）

```python
import os, sys

def _color_enabled(stream) -> bool:
    if os.environ.get("NO_COLOR"):        # https://no-color.org
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return bool(getattr(stream, "isatty", None) and stream.isatty())

class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        if not _color_enabled(sys.stdout):
            return message
        color = self.COLORS.get(record.levelname, self.COLORS["INFO"])
        return f"{color}{message}{self.COLORS['RESET']}"
```

这样管道捕获时自动得到干净文本，终端里仍有颜色。

### 2. 让 stream 动态解析

```python
class LazyStdoutHandler(logging.StreamHandler):
    """每次 emit 时动态取 sys.stdout，避免 import 期绑定导致重定向失效。"""

    def __init__(self, level=logging.NOTSET):
        logging.Handler.__init__(self, level)   # 跳过 StreamHandler 的绑定

    @property
    def stream(self):
        return sys.stdout

    @stream.setter
    def stream(self, value):
        pass
```

### 3. 关闭传播

在 `setup_logger` 里加一行 `logger.propagate = False`，避免与用户的
`basicConfig` 冲突产生双份输出。

### 4. 调用方侧：清洗颜色码

不管库改不改，消费方都建议备一个清洗函数：

```python
import re
ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)

# 用法
clean = strip_ansi(result.stdout)
assert "02:18:20 处理中" in clean
```

### 5. 子进程统一编码

```python
env = dict(os.environ, PYTHONIOENCODING="utf-8")
r = subprocess.run([...], capture_output=True, text=True,
                   encoding="utf-8", env=env)
if r.stdout is None:        # 防御：解码线程异常时 stdout 会是 None
    raise RuntimeError("子进程输出解码失败，检查编码设置")
```

---

## 九、速查表

| 你想做的事 | 做法 |
|------------|------|
| 捕获后做字符串断言 | 先 `strip_ansi()`，或用不带 `level` 的 `print` 路径 |
| 写入日志文件 | 用 `NO_COLOR=1` 环境变量，或清洗后再写 |
| 用 `capsys` / `redirect_stdout` 测试 | 先改 lazy stream handler，否则抓不到 |
| 保证中文不丢 | 子进程 `PYTHONIOENCODING=utf-8` + 父进程 `encoding="utf-8"` |
| 排查"日志不见了" | 看 stderr 里有没有 `--- Logging error ---` |
| 拿到 `None` 的 stdout | 说明解码线程炸了，检查子进程编码 |

---

## 附：复现实验的模块加载方式

`funcguard/__init__.py` 会引入 `requests`、`curl_cffi`、`pandas` 等依赖。
若环境未安装，可用 `importlib` 直接加载真实模块绕过 `__init__`：

```python
import importlib.util, sys, types

FUNC_DIR = r"<project>\funcguard"
pkg = types.ModuleType("funcguard")
pkg.__path__ = [FUNC_DIR]
sys.modules["funcguard"] = pkg

def _load(name):
    spec = importlib.util.spec_from_file_location(
        f"funcguard.{name}", f"{FUNC_DIR}\\{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[f"funcguard.{name}"] = mod
    spec.loader.exec_module(mod)
    return mod

log_utils = _load("log_utils")
time_utils = _load("time_utils")
```
