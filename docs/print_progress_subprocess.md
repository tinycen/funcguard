# print_progress 在 subprocess 中的打印行为与测试

本文记录对 `funcguard/printer.py` 中 `print_progress` 的一次完整排查：它在
`subprocess` 场景下到底能不能打印、被父进程捕获到的是什么形态、现有测试文件是否可信，
以及最终如何重写 `tests/test_print_progress.py`。

> 排查环境：Windows 11 / Python 3.13.14 / funcguard 工作区
> 项目约束：`setup.py` 中 `python_requires='>=3.10'`，CI 测试矩阵 `3.10 ~ 3.14`
>
> 相关文档：[time_log 彩色日志在 subprocess 中的输出与捕获](./time_log_subprocess.md)
> —— 讨论 ANSI 颜色码残留、编码静默失败等日志侧问题

---

## 结论速览

| 问题 | 结论 |
|------|------|
| subprocess 能捕获到进度条吗？ | **能**，每一帧内容都完整，一帧不漏 |
| 捕获到的是"一条横线"还是"多行"？ | **多行**。`\r` 被翻译成 `\n`，11 次刷新变成 11 行 |
| 每帧是完整的 50 格进度条吗？ | 是，每帧都是一次完整快照（不是只拿到最后一条） |
| 原测试文件正确吗？ | 8 个用例全绿，但**有 1 个语法级硬伤 + 1 个假通过用例** |
| `flush=True` 能被可靠验证吗？ | 能，但必须用**流式读取 + 帧到达时间跨度**判定 |

---

## 一、print_progress 的工作原理

`funcguard/printer.py:30` 的核心就一行：

```python
print(f"\r进度: |{bar}| {percent}% ({idx}/{total}) {message}", end='', flush=True)
```

三个关键设计：

| 要素 | 作用 |
|------|------|
| `\r` | 回车符，把光标挪回行首，实现**原地覆盖**刷新 |
| `end=''` | 不换行，保证所有帧停留在同一行 |
| `flush=True` | 立即刷新，绕过管道下的块缓冲（8KB），保证实时可见 |

进度条本体是 `'█' * (percent // 2) + '-' * (50 - percent // 2)`，固定 50 字符宽。

**这套机制只在真实终端（tty）里有效。** 终端有"光标"概念，收到 `\r` 会真的回到行首覆盖；
而 `subprocess.PIPE` 只是一根字节流管道，`\r` 在那里没有覆盖语义，仅仅是一个 `0x0D` 字节。

---

## 二、subprocess 捕获到的三种形态（实测）

测试脚本：循环调用 `print_progress(i, 10, "处理中")`，`i` 从 0 到 10，共 11 帧。

### 形态 ①：子进程写出的原始字节流

```
\r进度: |---...---| 0% (0/10) 处理中\r进度: |███---...| 10% (1/10) 处理中\r...\r进度: |███...███| 100% (10/10) 处理中
```

- `\r` 个数：**11**
- `\n` 个数：**0**
- 物理上是**一整行**，靠 `\r` 分隔出 11 帧

### 形态 ②：终端里看到的（对比用）

原地覆盖刷新，始终只有 1 行，只显示最后一帧：

```
进度: |██████████████████████████████████████████████████| 100% (10/10) 处理中
```

### 形态 ③：`capture_output=True, text=True`

```python
result = subprocess.run([sys.executable, "-c", script],
                        capture_output=True, text=True, encoding="utf-8")
```

实际拿到的 `result.stdout`（`repr` 截断展示）：

```
'\n进度: |--------------------------------------------------| 0% (0/10) 处理中\n进度: |█████---...| 10% (1/10) 处理中\n...\n进度: |███...███| 100% (10/10) 处理中'
```

- `\r` 个数：**0**
- `\n` 个数：**11**
- 行数：**12 行**（因为首字符就是 `\r`，被转换后开头多出一个空行）

打印出来的效果：

```
（空行）
进度: |--------------------------------------------------| 0% (0/10) 处理中
进度: |█████---------------------------------------------| 10% (1/10) 处理中
进度: |██████████----------------------------------------| 20% (2/10) 处理中
进度: |███████████████-----------------------------------| 30% (3/10) 处理中
进度: |████████████████████------------------------------| 40% (4/10) 处理中
进度: |█████████████████████████-------------------------| 50% (5/10) 处理中
进度: |██████████████████████████████--------------------| 60% (6/10) 处理中
进度: |███████████████████████████████████---------------| 70% (7/10) 处理中
进度: |████████████████████████████████████████----------| 80% (8/10) 处理中
进度: |█████████████████████████████████████████████-----| 90% (9/10) 处理中
进度: |██████████████████████████████████████████████████| 100% (10/10) 处理中
```

**根因**：`text=True` 会启用**通用换行转换**（universal newlines），把 `\r`、`\n`、`\r\n`
一律规范化成 `\n`。这是 Python 的标准行为，不是 bug，但会彻底改变进度条的呈现形态。

### 三种形态对照

| 捕获方式 | `\r` | `\n` | 行数 | 适用场景 |
|---------|------|------|------|---------|
| 终端直连（tty） | — | — | 1 行 | 人工观察 |
| `text=True` | 0 | 11 | 12 行 | 需要按行处理、写日志 |
| 二进制（不指定 `text`） | 11 | 0 | 1 行 | 需要还原 `\r` 语义 |

---

## 三、原测试文件审查

`tests/test_print_progress.py` 原有 8 个用例，本地（Python 3.13）**全部通过**。但审查发现 4 个问题。

### 问题 1：f-string 表达式内带反斜杠（严重，会导致 CI 失败）

原第 98 行：

```python
assert result.stdout.count("\r") == 3, (
    f"期望输出包含 3 个回车符（与调用次数一致），实际: {result.stdout.count("\\r")} 个，"
    f"输出: {repr(result.stdout)}"
)
```

在 f-string 的表达式部分出现反斜杠，是 **Python 3.12+（PEP 701）** 才允许的语法。
本项目 `python_requires='>=3.10'`，且 `.github/workflows/release.yml` 的测试矩阵包含
`3.10` 和 `3.11` —— 在这两个版本上整个文件会 **SyntaxError 直接导入失败**。
本地 3.13 能跑纯属侥幸。

**修复**：先把回车符取成变量，表达式里就不再有反斜杠。

```python
cr = "\r"
cr_count = result.stdout.count(cr)
assert cr_count == 3, (
    f"期望输出包含 3 个回车符（与调用次数一致），实际: {cr_count} 个，"
    f"输出: {repr(result.stdout)}"
)
```

### 问题 2：flush 测试是假通过

原 `test_print_progress_flushing_works_in_subprocess`：

```python
for i in range(5):
    print_progress(i, 4)
...
assert result.stdout.strip() != "", "期望有输出内容，但 stdout 为空"
assert "80%" in result.stdout or "100%" in result.stdout, ...
```

两个毛病：

1. **断言无效**。实测：不带 `flush` 的写入，在进程退出时一样会被 `capture_output`
   完整捕获（返回 `'X0X1X2'`）。所以 `stdout.strip() != ""` 根本证明不了 flush 生效，
   去掉 `flush=True` 这个用例照样绿。
2. **死分支**。`range(5)` 配 `total=4` 只会产出 `0% / 25% / 50% / 75% / 100%`，
   `"80%"` 永不命中。

### 问题 3：raw 分支硬编码 UTF-8 解码

原实现中二进制捕获后用 `encoding="utf-8"` 解码，但没约束子进程的编码。
在非 UTF-8 locale 的机器（中文 Windows 默认 GBK）上，子进程写出 GBK 字节、
父进程按 UTF-8 解码会抛 `UnicodeDecodeError`。

**修复**：统一给子进程注入 `PYTHONIOENCODING=utf-8`，两端编码钉死。

### 问题 4：缺少真实 `.py` 脚本场景

原实现全部用 `python -c` 内联代码，没有覆盖"运行一个真实脚本文件"这一最常见的用法。

---

## 四、重写后的测试文件设计

文件：`tests/test_print_progress.py`（11 个用例，全部通过）

### 核心 helper

| 函数 | 作用 |
|------|------|
| `_temp_script(source)` | 把源码写成真实 `.py` 临时文件，contextmanager 自动清理 |
| `_run_subprocess_script(script, raw)` | 以 `-c` 内联代码方式执行并捕获 |
| `_run_script_file(script, raw)` | **以真实 `.py` 文件方式**执行并捕获 |
| `_stream_script_file(script, timeout)` | `Popen(bufsize=0)` 逐字节读，记录每帧到达时刻 |

关键实现点：

```python
# 固定子进程 IO 编码，保证父进程可以安全地按 utf-8 解码
CHILD_ENV = dict(os.environ, PYTHONIOENCODING="utf-8")

# raw 模式：用 newline='' 阻止 \r -> \n 转换
stdout_text = io.TextIOWrapper(
    io.BytesIO(proc.stdout), encoding="utf-8", newline=""
).read()
```

### 用例清单

| # | 用例 | 验证点 |
|---|------|--------|
| 1 | `test_print_progress_basic_output_in_subprocess` | 基本输出含 50% / (5/10) / 分隔符 |
| 2 | `test_print_progress_contains_carriage_return` | raw 模式下 `\r` 数量为 3 |
| 3 | `test_print_progress_full_cycle_in_subprocess` | 完整循环最终到 100% (10/10) |
| 4 | `test_print_progress_bar_characters` | 填充字符 `█` |
| 5 | `test_print_progress_zero_percent` | 0% 边界 |
| 6 | `test_print_progress_with_message` | 自定义消息 |
| 7 | `test_print_progress_invalid_total` | `total=0` 走警告分支 |
| 8 | `test_print_progress_in_real_py_file` | **真实 .py 脚本**完整输出 |
| 9 | `test_print_progress_in_real_py_file_keeps_carriage_return` | **真实 .py 脚本**保留 `\r` |
| 10 | `test_print_progress_streams_in_realtime` | **flush 真正生效**（帧跨度判定） |
| 11 | `test_print_progress_stream_frames_split_by_carriage_return` | 按 `\r` 切帧，每帧完整 |

---

## 五、验证 flush 的正确姿势（含一次踩坑）

### 踩坑：用"子进程是否存活"判定有竞态

第一版实现是"首字节到达时检查 `proc.poll() is None`"。做完变异测试（临时去掉
`flush=True`）后发现**用例仍然通过**。

原因：子进程退出瞬间才把缓冲区刷出去，父进程收到字节后调用 `poll()` 时，
子进程可能还没完全退出，`poll()` 返回 `None`，被误判成"实时输出"。

### 正解：测帧到达时间跨度

逐字节读取，每遇到一个 `\r`（新一帧的开始）就记录时刻，最后算首尾帧的时间跨度：

```python
while time.monotonic() < deadline:
    chunk = proc.stdout.read(1)      # bufsize=0，有数据立刻返回
    if not chunk:
        break
    if chunk == b"\r":
        frame_times.append(time.monotonic())
    chunks.append(chunk)

spread = frame_times[-1] - frame_times[0]
assert spread > 1.0, f"进度帧几乎同时到达（跨度仅 {spread:.3f}s），flush 未生效"
```

这个判据不受解释器启动耗时和机器性能影响，**跨机器稳定**。

### 变异测试结果

脚本：5 帧，每帧后 `sleep(0.4)`，理论跨度约 1.6s。

| 场景 | 首字节到达 | 帧跨度 | 用例结果 |
|------|-----------|--------|---------|
| 有 `flush=True` | 0.670s | ≈1.6s | ✓ 通过 |
| 去掉 `flush=True` | 2.705s | **0.001s** | ✗ 失败 |

失败信息：

```
✗ 流式实时输出(flush): 进度帧几乎同时到达（跨度仅 0.001s），说明输出被缓冲到进程退出才刷出，flush=True 未生效
```

> 另一次对照实验（5 帧 × `sleep(0.3)`）：有 flush 首字节 0.610s，无 flush 2.164s，
> 趋势一致。首字节耗时里约 0.6s 是 Windows 上 Python 解释器的启动开销，
> 这也是为什么判据要用"帧跨度"而不是"首字节绝对耗时"。

---

## 六、编码陷阱速查

```python
# 危险：text=True 默认用 locale 编码
# 中文 Windows 上是 GBK，子进程写 UTF-8 的 '█' 会乱码或 UnicodeDecodeError
subprocess.run([...], capture_output=True, text=True)

# 安全：两端都钉死 UTF-8
env = dict(os.environ, PYTHONIOENCODING="utf-8")
subprocess.run([...], capture_output=True, text=True,
               encoding="utf-8", env=env)
```

实测 `PYTHONIOENCODING=gbk` 时 `█` 会被编码成 `b'\xa8\x80'`（GBK 收录了 U+2588，
所以不会报错，但父进程若按 UTF-8 解码仍然会炸 —— 属于静默风险，更值得警惕）。

---

## 七、printer.py 的既有缺陷（待确认是否修复）

### 1. `idx > total` 时进度条溢出

```python
print_progress(15, 10)
# 进度: |████...████| 150% (15/10)   ← 实际 75 个字符，超出设计的 50
```

`percent=150` 时 `'-' * (50 - 75)` 得到空串，条子长度变成 `150 // 2 = 75`。
建议钳制：`percent = max(0, min(100, int(idx / total * 100)))`。

### 2. `\r` 只覆盖不清行

进度回退、或 `message` 变短时，上一帧的残留字符会留在屏幕上。
常规做法是先写 `\r` + 等长空格 + `\r`，或用 ANSI 的 `\033[K`（清行尾）。

### 3. 不感知非 tty 环境

`tqdm` / `rich` 会检测 `sys.stdout.isatty()`，在非终端环境自动降级为
"每隔 N 次打一行"或干脆不画动态条。`print_progress` 没有这个判断，
在 CI 日志、重定向到文件的场景下会把日志刷爆。

---

## 八、最佳实践清单

**只想拿到最终状态（写日志 / 上报告警）：**

```python
r = subprocess.run([...], capture_output=True, text=True, encoding="utf-8")
last = r.stdout.strip().splitlines()[-1]     # 只留 100% 那一帧
```

**想保留"一行刷新"的原始语义：**

```python
r = subprocess.run([...], capture_output=True)        # 不指定 text
frames = r.stdout.decode("utf-8").split("\r")         # 11 帧
```

**想边跑边看实时进度：**

```python
proc = subprocess.Popen([...], stdout=subprocess.PIPE, bufsize=0)
while (chunk := proc.stdout.read(1)):
    sys.stdout.buffer.write(chunk)
    sys.stdout.buffer.flush()
```

**写测试断言时：**

- 验证 `\r` 必须走二进制 + `newline=""`，`text=True` 会把它吃掉
- 验证 `flush` 必须用流式读取 + 帧跨度，不要用 `capture_output`
- 跑完记得做一次变异测试，确认用例真的能失败

---

## 附：完整运行输出

```
============================================================
测试 print_progress 在 subprocess 中的打印功能
============================================================
  ✓ 基本输出
  ✓ 回车符检查
  ✓ 完整进度循环
  ✓ 进度条字符
  ✓ 0% 进度
  ✓ 自定义消息
  ✓ 非法 total 值
  ✓ 真实 .py 脚本
  ✓ 真实 .py 脚本保留回车符
  ✓ 流式实时输出(flush)
  ✓ 流式按回车符切帧
------------------------------------------------------------
结果: 11 通过, 0 失败
```

去掉 `flush=True` 后的变异测试输出：

```
  ✓ 基本输出
  ...
  ✗ 流式实时输出(flush): 进度帧几乎同时到达（跨度仅 0.001s），说明输出被缓冲到进程退出才刷出，flush=True 未生效
  ✓ 流式按回车符切帧
------------------------------------------------------------
结果: 10 通过, 1 失败
```
