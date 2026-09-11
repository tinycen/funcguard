# subprocess 场景下的输出行为（0.3.0+）

本文说明 funcguard 各输出函数在 `subprocess`（管道捕获）场景下的**当前行为**，
以及调用侧的推荐写法。0.3.0 之前的旧行为排查记录见
[重构记录/subprocess输出问题排查](./重构记录/subprocess输出问题排查/fix_plan.md)。

## 各函数的管道捕获形态

| 函数 | 管道（非 tty）下的输出 | 说明 |
|------|----------------------|------|
| `print_progress` | 按 10% 步进的换行行（`0% → 100%` 共 11 行），无 `\r` | 自动降级，不刷屏、可按行解析 |
| `time_log` | `HH:MM:SS 消息`（北京时间），无 ANSI 颜色码 | 统一走 logger，`emit` 自动 flush |
| `time_wait` | 每秒一行 `Time wait: Ns` | 自动降级 |
| `time_diff` / `print_title` / `print_line` / `print_block` | 原样换行输出 | 全部带 `flush=True` |
| `setup_logger` 创建的 logger | 纯文本（无 ANSI），时间格式/时区按 `format`/`datefmt`/`tz` 配置 | tty 感知自动降级 |

共同点：**所有输出在写入时即 flush**，不经过用户态块缓冲——子进程即使被
kill（OOM、信号），已打印的内容也完整保留在管道里，不会整条丢失。

## 调用侧推荐写法

```python
import os, subprocess, sys

env = dict(os.environ,
    PYTHONUNBUFFERED="1",       # （可选）子进程 stdout/stderr 不缓冲
    PYTHONIOENCODING="utf-8")   # 两端编码钉死，防 GBK/cp1252 静默吞日志

proc = subprocess.Popen(
    [sys.executable, "worker.py"],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,       # 合并 stderr，报错链条与上下文同序
    bufsize=0,                      # unbuffered raw：read 按块立即返回
    env=env,
)
while chunk := proc.stdout.read(4096):   # 按块读而非按行读，实时性最好
    sys.stdout.buffer.write(chunk)
    sys.stdout.buffer.flush()
rc = proc.wait()
```

要点：

- **`PYTHONUNBUFFERED=1` 不再是必需的**：funcguard 的所有输出已自带 flush；
  但如果子进程里还有你自己写的其他 `print(...)`（无 flush），仍建议加上兜底
- **编码钉死**：子进程 `PYTHONIOENCODING=utf-8` + 父进程 `encoding="utf-8"`（或
  二进制捕获后自行 decode），防止中文内容在编码不匹配时被静默吞掉
- **按块读优于按行读**：`readline()` 对无换行的输出会阻塞；按块 `read(4096)`
  兼容所有形态
- **`text=True` 的换行转换**：会把 `\r\n`、`\r` 统一规范为 `\n`。funcguard 在
  管道下已不输出 `\r`，两种模式拿到的内容一致；需要原始字节就走二进制捕获

## 终端颜色的环境变量开关

- `NO_COLOR=1`：强制禁用颜色（[no-color.org](https://no-color.org) 标准）
- `FORCE_COLOR=1`：强制启用颜色（即使在管道中，优先级高于 tty 检测）

## 测试与调试

- `redirect_stdout` / pytest `capsys` 可正常捕获 funcguard 的 logger 输出
  （stream 在 emit 时动态解析，非 import 期绑定）
- 排查"日志不见了"：先看子进程 stderr 是否有 `--- Logging error ---`
  （编码失败时 logging 模块的提示），再检查两端的编码设置
