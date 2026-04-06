# FuncGuard

FuncGuard是一个Python库，提供了函数执行超时控制和重试机制的实用工具。
[![zread](icon/zread-badge.svg)](https://zread.ai/tinycen/funcguard)

## 功能特点

| 分类 | 功能描述 |
|------|----------|
| **核心功能** | 函数执行超时控制、函数执行失败自动重试 |
| **网络请求** | HTTP请求封装（支持自动重试）、MD5哈希、Basic Auth编码 |
| **时间工具** | 时间日志记录、耗时统计、执行时间监控和警告、时间等待（带倒计时） |
| **打印工具** | 格式化分隔线、块打印、标题打印、进度条显示 |
| **IP工具** | 局域网IP检测、公网IP检测、IP格式验证 |
| **pandas工具** | 数据填充、类型转换、JSON解析、数据筛选、统计分析 |
| **计算工具** | 数值差异格式化（如+5、-3等） |
| **日志工具** | 彩色日志输出、logger配置 |

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

使用`print_line`、`print_block`、`print_title`和`print_progress`函数进行格式化打印，便于查看和调试：

```python
from funcguard import print_line, print_block, print_title, print_progress

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

# 打印进度条
for i in range(101):
    import time
    time.sleep(0.05)  # 模拟处理时间
    print_progress(i, 100, "处理中")  # 显示进度条和处理状态
print()  # 处理完成后换行
```

### 时间日志记录

- 自动显示北京时间（UTC+8）
- 支持进度显示和预计完成时间计算
- 提供中英文双语统计信息
- 可显示总耗时、平均耗时等详细统计
- 支持i从0或从1开始的计数方式
- 支持 level 参数输出彩色日志（DEBUG/INFO/PROGRESS/SUCCESS/WARNING/WARN/ERROR/CRITICAL/FATAL）
- 支持函数执行时间监控和警告

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
      # 使用 level 输出彩色日志
      time_log("处理进度", i, 100, start_time, 0, level="progress")  # 显示进度和预计完成时间

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
      time_log("处理进度", i, 100, start_time, 1, level="progress")  # 显示进度和预计完成时间

```

### 组合示例用法

在实际应用中，可以组合使用`time_log`和`print_progress`来显示处理进度和剩余时间：

```python
from funcguard import time_diff, time_log, print_progress
import pandas as pd

def process_images(images):
    """处理图片的示例函数"""
    # 模拟图片处理
    import time
    time.sleep(0.1)
    return f"processed_{images}"

# 假设df是一个包含图片数据的DataFrame
df = pd.DataFrame({"images": [f"img_{i}.jpg" for i in range(100)]})

# 获取开始时间
s_time = time_diff() 
processed_images_list = [] 
max_num = len(df) 

# 处理每一行数据
for index, row in df.iterrows(): 
    processed_images_list.append(process_images(row["images"])) 
    
    # 获取剩余时间并显示进度条
    remaining_time = time_log("", index, max_num, s_time, return_field="remaining_time") 
    print_progress(index, max_num, remaining_time) 

# 更新DataFrame中的图片数据
df["images"] = processed_images_list 

# 打印处理完成后的统计信息
time_diff(s_time, max_num)
```

这个组合示例展示了如何：
1. 使用`time_diff()`获取开始时间
2. 在循环中使用`time_log`获取剩余时间（通过`return_field="remaining_time"`参数）
3. 使用`print_progress`显示进度条和剩余时间
4. 最后使用`time_diff`打印完整的处理统计信息

### 时间等待

使用`time_wait`函数进行带倒计时显示的时间等待：

```python
from funcguard import time_wait

# 等待10秒，显示倒计时
print("开始等待...")
time_wait(10)  # 显示倒计时：Time wait: 10s, 9s, 8s...
print("等待完成！")

# 等待5秒
print("准备开始下一步操作...")
time_wait(5)
print("开始执行下一步操作")
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

### log 日志工具

使用`setup_logger`函数多彩显示日志：

```python
from funcguard import setup_logger

# 在 network.py
logger_a = setup_logger("network")
logger_a.debug("网络调试信息")

# 在 db.py
logger_b = setup_logger("db")
logger_b.debug("数据库调试信息")

# 全局 loggeer
logger = setup_logger()
logger.debug("网络调试信息")
logger.debug("数据库调试信息")

# 设置等级 level : 字符串（大小写不敏感）
logger = setup_logger(level="debug")

# 仅输出消息（不包含时间与等级）
logger = setup_logger(message_only=True)

# 支持的输出（含颜色）
logger.debug("这是一条调试信息")      # 青色
logger.info("这是一条普通信息")       # 白色/浅灰色/默认
logger.success("这是一条成功信息")    # 绿色
logger.progress("这是一条进度信息")   # 蓝色
logger.warning("这是一条警告信息")    # 黄色
logger.error("这是一条错误信息")      # 红色
logger.critical("这是一条严重错误信息")  # 紫色

# 注意：Windows 自带终端（旧版 CMD）可能不支持 ANSI 颜色码

```


### IP地址检测

使用IP检测功能获取本机局域网IP、公网IP以及验证IP地址格式：

```python
from funcguard import get_local_ip, get_public_ip, get_ip_info, is_valid_ip

# 获取本机局域网IP地址
local_ip = get_local_ip()
print(f"本机局域网IP: {local_ip}")

# 获取本机公网IP地址
public_ip = get_public_ip()
print(f"本机公网IP: {public_ip}")

# 获取完整的IP信息（包括局域网IP、公网IP和主机名）
ip_info = get_ip_info()
print(f"主机名: {ip_info['hostname']}")
print(f"局域网IP: {ip_info['local_ip']}")
print(f"公网IP: {ip_info['public_ip']}")

# 验证IP地址格式是否有效
test_ips = ["192.168.1.1", "256.1.1.1", "abc.def.ghi.jkl"]
for ip in test_ips:
    is_valid = is_valid_ip(ip)
    print(f"IP地址 '{ip}' 验证结果: {is_valid}")
```

### pandas数据处理工具

FuncGuard提供了丰富的pandas数据处理功能，包括数据填充、类型转换、JSON处理、统计分析等。详细使用方法请参考[pd_utils文档](docs/pd_utils.md)。

```python
import pandas as pd
from funcguard.pd_utils import fill_na, convert_columns, round_columns, load_json

# 快速示例
df = pd.DataFrame({
    'name': ['张三', '李四', None, '王五'],
    'age': [25.7, 30.2, 28.9, 35.1],
    'config': ['{"timeout": 30}', '{"timeout": 60}', '', '{"timeout": 90}']
})

# 数据填充
df = fill_na(df, {'name': '未知'})

# 类型转换
df = convert_columns(df, {'age': 'int'})

# JSON解析
df = load_json(df, ['config'])
```

### 数值差异格式化

使用`format_difference`函数格式化两个数值之间的差异，常用于显示数值变化：

```python
from funcguard import format_difference

# 计算并格式化数值变化
old_value = 100
new_value = 150
print(format_difference(old_value, new_value))  # 输出: +50

old_value = 200
new_value = 180
print(format_difference(old_value, new_value))  # 输出: -20

old_value = 100
new_value = 100
print(format_difference(old_value, new_value))  # 输出: (空字符串)

# 在实际应用中的示例
current_price = 150.5
previous_price = 145.2
price_change = format_difference(previous_price, current_price)
print(f"当前价格: {current_price}, 变化: {price_change}")  # 输出: 当前价格: 150.5, 变化: +5.3
```

## 详细功能列表

### 核心功能

| 函数/类名 | 功能说明 |
|-----------|----------|
| `timeout_handler` | 函数执行超时控制 |
| `retry_function` | 函数执行失败自动重试 |

### 网络请求

| 函数/类名 | 功能说明 |
|-----------|----------|
| `send_request` | HTTP请求封装（支持自动重试） |
| `curl_cffi_request` | 使用curl_cffi发送HTTP请求 |
| `md5_hash` | MD5哈希计算 |
| `encode_basic_auth` | Basic Auth编码 |

### 时间工具

| 函数/类名 | 功能说明 | 文档 |
|-----------|----------|------|
| `time_log` | 时间日志记录（支持彩色输出） | [查看](docs/time_utils.md#time_log) |
| `time_diff` | 耗时统计和计算 | [查看](docs/time_utils.md#time_diff) |
| `time_monitor` | 函数执行时间监控和警告 | [查看](docs/time_utils.md#time_monitor) |
| `time_wait` | 时间等待（带倒计时显示） | [查看](docs/time_utils.md#time_wait) |
| `get_now` | 获取当前时间 | - |
| `generate_timestamp` | 生成时间戳 | - |
| `cal_date_diff` | 计算日期差异 | - |

### 打印工具

| 函数/类名 | 功能说明 |
|-----------|----------|
| `print_line` | 打印分隔线 |
| `print_block` | 打印块内容 |
| `print_title` | 打印标题 |
| `print_progress` | 打印进度条 |

### IP工具

| 函数/类名 | 功能说明 |
|-----------|----------|
| `get_local_ip` | 获取局域网IP |
| `get_public_ip` | 获取公网IP |
| `get_ip_info` | 获取完整IP信息 |
| `is_valid_ip` | 验证IP格式 |

### pandas工具

| 函数/类名 | 功能说明 | 文档 |
|-----------|----------|------|
| `pd_fill_na` / `pd_fill_nat` | 数据填充 | [查看](docs/pandas/fill.md) |
| `pd_convert_columns` / `pd_convert_decimal` / `pd_convert_numeric_series` / `pd_convert_str_datetime` / `pd_convert_datetime_str` | 类型转换 | [查看](docs/pandas/convert.md) |
| `pd_load_json` | JSON解析 | [查看](docs/pandas/json.md) |
| `pd_filter` / `pd_count` | 数据筛选 | [查看](docs/pandas/filter.md) |
| `pd_build_mask` / `pd_build_masks` / `pd_combine_masks` | 掩码构建 | [查看](docs/pandas/mask.md) |
| `DataFrameStatistics` | 统计分析 | [查看](docs/pandas/statistics.md) |
| `pd_cal_date_diff` / `pd_round_columns` | 日期计算和数值舍入 | [查看](docs/pandas/date.md) |

### 计算工具

| 函数/类名 | 功能说明 |
|-----------|----------|
| `format_difference` | 数值差异格式化 |

### 日志工具

| 函数/类名 | 功能说明 |
|-----------|----------|
| `setup_logger` | 配置彩色日志logger |
| `color_logger` | 彩色日志输出 |



## 许可证

MIT License