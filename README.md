# FuncGuard

FuncGuard是一个Python库，提供了函数执行超时控制和重试机制的实用工具。

## 功能特点

- 函数执行超时控制
- 函数执行失败自动重试
- HTTP请求封装（支持自动重试）

## 安装/升级

```bash
pip install funcguard
```

```bash
pip install --upgrade funcguard
```


## 使用方法

### 超时控制

使用`timeout_handler`函数可以控制函数的执行时间，防止函数运行时间过长：

```python
from funcguard.core import timeout_handler

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
from funcguard.core import retry_function

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
from funcguard.tools import send_request

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

## 许可证

MIT License