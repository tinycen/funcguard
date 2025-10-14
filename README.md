# FuncGuard

FuncGuard是一个Python库，提供了函数执行超时控制和重试机制的实用工具。

## 功能特点

- 函数执行超时控制
- 函数执行失败自动重试
- HTTP请求封装（支持自动重试）
- 格式化打印工具（分隔线和块打印）
- 时间日志记录和耗时统计
- 函数执行时间监控和警告

## 安装/升级

```bash
pip install --upgrade funcguard
```


## 使用方法

### 超时控制

使用`timeout_handler`函数可以控制函数的执行时间，防止函数运行时间过长：

```python
from funcguard import timeout_handler

def long_running_function():
    # 模拟一个耗时操作
    import time
    time.sleep(10)
    return "操作完成"

try:
    # 设置超时时间为5秒
    result = timeout_handler(long_running_function, execution_timeout=5)
    print(result)
except TimeoutError as e:
    print(f"捕获到超时错误: {e}")
```

### 重试机制

使用`retry_function`函数可以在函数执行失败时自动重试：

```python
from funcguard import retry_function

def unstable_function():
    # 模拟一个可能失败的操作
    import random
    if random.random() < 0.7:  # 70%的概率失败
        raise Exception("随机错误")
    return "操作成功"

try:
    # 最多重试3次，每次执行超时时间为10秒
    result = retry_function(unstable_function, max_retries=3, execute_timeout=10, task_name="测试任务")
    print(result)
except Exception as e:
    print(f"重试后仍然失败: {e}")
```

### HTTP请求

使用`send_request`函数发送HTTP请求，支持自动重试：

```python
from funcguard import send_request

# 不使用重试
response = send_request(
    method="GET",
    url="https://api.example.com/data",
    headers={"Content-Type": "application/json"},
    timeout=30
)
print(response)

# 使用重试
response = send_request(
    method="POST",
    url="https://api.example.com/data",
    headers={"Content-Type": "application/json"},
    data={"key": "value"},
    timeout=30,
    auto_retry={
        "task_name": "API请求",
        "max_retries": 3,
        "execute_timeout": 60
    }
)
print(response)
```

### 格式化打印

使用`print_line`、`print_block`和`print_title`函数进行格式化打印，便于查看和调试：

```python
from funcguard import print_line, print_block, print_title

# 打印带等号的标题
print_title("初始化分类器")  # 输出：=== 初始化分类器 ===
print_title("训练完成", separator_char="*", padding_length=2)  # 输出：** 训练完成 **

# 打印分隔线
print_line()  # 默认使用40个'-'字符
print_line("*", 30)  # 使用30个'*'字符

# 打印块内容
print_block("用户信息", {"name": "张三", "age": 25})

# 自定义分隔符
print_block("配置信息", {"debug": True, "port": 8080}, "=", 50)

# 打印复杂内容
result = {
    "status": "success",
    "data": [1, 2, 3, 4, 5],
    "message": "操作完成"
}
print_block("API响应", result)
```

### 时间日志记录

使用`time_log`和`time_diff`函数记录任务执行时间和统计信息：

```python
from funcguard import time_log, time_diff

# 获取开始时间
start_time = time_diff()

# 记录任务开始（i从0开始）
time_log("开始处理数据", 0, 100, start_time, 0)

# 模拟处理过程
import time
for i in range(1, 101):
    time.sleep(0.1)  # 模拟处理时间
    if i % 20 == 0:
        time_log(f"处理进度", i, 100, start_time, 0)  # 显示进度和预计完成时间

# 记录任务完成并打印统计信息
time_diff(start_time, 100, "cn")  # 中文显示统计信息
```

或者当i从1开始时：

```python

# 记录任务开始（i从1开始）
time_log("开始处理数据", 1, 100, start_time, 1)

# 模拟处理过程
import time
for i in range(1, 101):
    time.sleep(0.1)  # 模拟处理时间
    if i % 20 == 0:
        time_log(f"处理进度", i, 100, start_time, 1)  # 显示进度和预计完成时间

```

### 执行时间监控

使用`time_monitor`函数监控函数执行时间：

```python
from funcguard import time_monitor

def some_function():
    # 模拟一个耗时操作
    import time
    time.sleep(2)
    return "操作完成"

# 模式1：总是打印执行时间
result = time_monitor(
    func=some_function,
    print_mode=1
)
print(f"结果: {result}")

# 模式2：仅在超过阈值时打印警告
result = time_monitor(
    func=some_function,
    warning_threshold=1.5,  # 设置1.5秒的警告阈值
    print_mode=2
)
print(f"结果: {result}")

# 模式0：不打印任何信息，仅返回结果和执行时间
result, duration = time_monitor(
    func=some_function,
    print_mode=0
)
print(f"结果: {result}, 耗时: {duration}秒")
```

时间日志功能特点：
- 自动显示北京时间（UTC+8）
- 支持进度显示和预计完成时间计算
- 提供中英文双语统计信息
- 可显示总耗时、平均耗时等详细统计
- 支持i从0或从1开始的计数方式
- 支持函数执行时间监控和警告

## API文档

### funcguard.core

#### timeout_handler(func, args=(), kwargs=None, execution_timeout=90)

- **参数**:
  - `func`: 需要执行的目标函数
  - `args`: 目标函数的位置参数，默认为空元组
  - `kwargs`: 目标函数的关键字参数，默认为None
  - `execution_timeout`: 函数执行的超时时间，单位为秒，默认为90秒
- **返回值**: 目标函数的返回值
- **异常**: `TimeoutError` - 当函数执行超过指定时间时抛出

#### retry_function(func, max_retries=5, execute_timeout=90, task_name="", *args, **kwargs)

- **参数**:
  - `func`: 需要重试的函数
  - `max_retries`: 最大重试次数，默认为5
  - `execute_timeout`: 执行超时时间，默认为90秒
  - `task_name`: 任务名称，用于打印日志
  - `args`: func的位置参数
  - `kwargs`: func的关键字参数
- **返回值**: func的返回值
- **异常**: 当重试次数用尽后仍然失败时，抛出最后一次的异常

### funcguard.tools

#### send_request(method, url, headers, data=None, return_type="json", timeout=60, auto_retry=None)

- **参数**:
  - `method`: HTTP方法（GET, POST等）
  - `url`: 请求URL
  - `headers`: 请求头
  - `data`: 请求数据，默认为None
  - `return_type`: 返回类型，可选"json"、"response"或"text"，默认为"json"
  - `timeout`: 请求超时时间，单位为秒，默认为60
  - `auto_retry`: 自动重试配置，格式为`{"task_name": "", "max_retries": 5, "execute_timeout": 90}`，默认为None
- **返回值**: 根据return_type参数返回不同格式的响应数据
- **异常**: 当请求失败且重试次数用尽后，抛出相应的异常

### funcguard.time_utils

#### time_log(message, i=0, max_num=0, s_time=None, start_from=0)

- **参数**:
  - `message`: 日志消息
  - `i`: 当前进度，默认为0
  - `max_num`: 总进度数量，默认为0
  - `s_time`: 开始时间，用于计算预计完成时间，默认为None
  - `start_from`: i是否从0开始，0表示从0开始，1表示从1开始，默认为0
- **返回值**: 无
- **功能**: 打印带时间戳的日志信息，支持进度显示和预计完成时间计算

#### time_diff(s_time=None, max_num=0, language="cn", return_duration=1)

- **参数**:
  - `s_time`: 开始时间，默认为None
  - `max_num`: 任务数量，默认为0
  - `language`: 语言选择（"cn"中文，其他为英文），默认为"cn"
  - `return_duration`: 返回模式，默认为1:
    - 0 - 仅返回 total_seconds，不打印信息
    - 1 - 仅打印信息,不返回 total_seconds
    - 2 - 打印信息，并返回 total_seconds
- **返回值**: 
  - 如果s_time为None则返回当前时间
  - 如果return_duration为0或2则返回持续时间（秒）
  - 否则返回None
- **功能**: 计算并打印任务执行时间统计信息，支持中英文双语输出

#### time_monitor(warning_threshold=None, print_mode=2, func=None, *args, **kwargs)

- **参数**:
  - `warning_threshold`: 警告阈值（秒），如果执行耗时超过此值则打印警告，默认为None
  - `print_mode`: 打印模式，支持三种模式:
    - 0 - 仅返回total_seconds，不打印任何信息
    - 1 - 总是打印执行时间
    - 2 - 仅在超时打印警告信息（默认）
  - `func`: 要监控的函数
  - `args`: 函数的位置参数
  - `kwargs`: 函数的关键字参数
- **返回值**: 
  - print_mode == 0: 元组 (result, total_seconds) - 函数的执行结果和执行时间（秒）
  - print_mode == 1: 函数的执行结果
  - print_mode == 2: 函数的执行结果
- **功能**: 监控函数执行时间，并返回函数的执行结果和执行时间
- **注意**: 该方法内部使用 time_diff 函数，根据 print_mode 自动设置 return_duration 参数
  - print_mode 为 0 或 2 时，设置 return_duration=0（ time_diff 仅返回total_seconds，不打印信息）
  - print_mode 为 1 时，设置 return_duration=2（ time_diff 打印信息，并返回total_seconds）

### funcguard.printer

#### print_line(separator_char: str = "-", separator_length: int = 40) -> None

- **参数**:
  - `separator_char`: 分隔符字符，默认为'-'
  - `separator_length`: 分隔符长度，默认为40
- **返回值**: 无
- **功能**: 打印分隔线，用于分隔不同的打印块

#### print_title(title: str, separator_char: str = "=", padding_length: int = 3) -> None

- **参数**:
  - `title`: 标题内容
  - `separator_char`: 分隔符字符，默认为'='
  - `padding_length`: 标题两侧的分隔符数量，默认为3
- **返回值**: 无
- **功能**: 打印带分隔符的标题，格式如：=== 初始化分类器 ===

#### print_block(title: str, content: Any, separator_char: str = "-", separator_length: int = 40) -> None

- **参数**:
  - `title`: 标题
  - `content`: 打印的内容
  - `separator_char`: 分隔符字符，默认为'-'
  - `separator_length`: 分隔符长度，默认为40
- **返回值**: 无
- **功能**: 使用分隔符打印标题和内容，便于查看

## 许可证

MIT License