# FuncGuard

FuncGuard是一个Python库，提供了函数执行超时控制和重试机制的实用工具。
[![zread](icon/zread-badge.svg)](https://zread.ai/tinycen/funcguard)

## 功能特点

- 函数执行超时控制
- 函数执行失败自动重试
- HTTP请求封装（支持自动重试）
- 格式化打印工具（分隔线和块打印）
- 进度条显示功能
- 时间日志记录和耗时统计
- 函数执行时间监控和警告
- IP地址检测（局域网IP和公网IP）
- 时间等待功能（带倒计时显示）
- pandas数据处理工具（空值填充、列类型转换、Decimal转换、JSON字符串转换等）
- 数值差异格式化工具（格式化数值变化，如+5、-3等）

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

使用pandas工具进行数据处理和类型转换：

```python
import pandas as pd
from funcguard import pd_fill_null, pd_round_columns, pd_convert_columns, pd_convert_decimal
from decimal import Decimal

# 创建示例DataFrame
df = pd.DataFrame({
    'name': ['张三', '李四', None, '王五'],
    'age': [25.7, 30.2, 28.9, 35.1],
    'salary': [Decimal('5000.50'), Decimal('6000.75'), Decimal('5500.25'), Decimal('7000.00')],
    'score': [85.678, 92.345, 78.901, 88.234],
    'join_date': ['2023-01-15', '2023-02-20', '2023-03-10', '2023-04-05']
})

# 1. 填充空值
df = pd_fill_null(df, {'name': '未知'}, None)  # 将name列的空值填充为'未知'

# 2. 四舍五入指定列
df = pd_round_columns(df, ['age'], 0)  # 将age列四舍五入到整数

# 3. 转换列数据类型
df = pd_convert_columns(df, {
    'age': 'int',
    'join_date': 'datetime',
    'name': 'str'
})

# 4. 转换Decimal类型
df = pd_convert_decimal(df, ['salary'], 'float')  # 将salary列的Decimal转换为float

# 5. 批量处理多个列
df = pd_fill_null(df, ['score'], 0)  # 将score列的空值填充为0
df = pd_round_columns(df, ['score'], 1)  # 将score列四舍五入到1位小数

print(df)
print(df.dtypes)
```

### JSON字符串转换

使用`pd_load_json`函数将DataFrame中的JSON字符串列转换为Python对象：

```python
import pandas as pd
from funcguard import pd_load_json

# 创建包含JSON字符串的示例DataFrame
df = pd.DataFrame({
    'id': [1, 2, 3],
    'config': ['{"timeout": 30, "retry": 3}', '{"timeout": 60, "retry": 5}', ''],
    'metadata': ['{"version": "1.0", "env": "prod"}', '', '{"version": "2.0", "env": "dev"}']
})

# 将JSON字符串列转换为Python对象
df = pd_load_json(df, ['config', 'metadata'])

# 现在可以直接访问转换后的对象
print(df['config'][0]['timeout'])  # 输出: 30
print(df['metadata'][2]['version'])  # 输出: 2.0

# 处理空字符串（默认转换为{}）
print(df['config'][2])  # 输出: {}
print(df['metadata'][1])  # 输出: {}
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

#### encode_basic_auth(username, password)

- **参数**:
  - `username`: 用户名字符串
  - `password`: 密码字符串
- **返回值**: 用于HTTP Basic认证的Authorization头部字符串，格式为`Basic xxxxx`（base64编码）
- **功能**: 生成符合HTTP Basic认证要求的Authorization头部内容，常用于需要用户名和密码认证的HTTP请求。

#### send_request(method, url, headers=None, data=None, return_type="json", timeout=60, auto_retry=None)

- **参数**:
  - `method`: HTTP方法（GET, POST等）
  - `url`: 请求URL
  - `headers`: 请求头，默认为None。若未传入且`data`为非空dict，则自动添加`Content-Type: application/json`。
  - `data`: 请求数据，默认为None。支持dict、list、str等类型。若为dict或list会自动转为JSON字符串。
  - `return_type`: 返回类型，可选"json"、"response"或"text"，默认为"json"
  - `timeout`: 请求超时时间，单位为秒，默认为60
  - `auto_retry`: 自动重试配置，格式为`{"task_name": "", "max_retries": 5, "execute_timeout": 90}`，默认为None
- **返回值**: 根据return_type参数返回不同格式的响应数据
- **异常**: 当请求失败且重试次数用尽后，抛出相应的异常
- **注意**:
  - 当`headers`为None且`data`为非空dict时，会自动设置`Content-Type: application/json`。
  - 若已传入`headers`且未包含`Content-Type`，且`data`为非空dict，也会自动补充`Content-Type: application/json`。
  - `data`为list类型时不会自动补充`Content-Type: application/json`，如需请自行传入headers。
  - 其他类型的`data`（如str、bytes）将直接作为请求体发送。

### funcguard.time_utils

#### time_log(message, i=0, max_num=0, s_time=None, start_from=0, return_field="progress_info")

- **参数**:
  - `message`: 日志消息
  - `i`: 当前进度，默认为0
  - `max_num`: 总进度数量，默认为0
  - `s_time`: 开始时间，用于计算预计完成时间，默认为None
  - `start_from`: i是否从0开始，0表示从0开始，1表示从1开始，默认为0
  - `return_field`: 返回字段，支持以下：
    - "progress_info" 表示完整进度信息（默认）
    - "remaining_time" 表示剩余时间
    - "end_time" 表示预计完成时间
- **返回值**: 
  - 根据return_field参数返回不同的信息
  - 默认情况下打印带时间戳的日志信息并返回进度信息
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

#### time_wait(seconds: int = 10)

- **参数**:
  - `seconds`: 等待的秒数，默认值为10秒
- **返回值**: 无
- **功能**: 等待指定的秒数，显示倒计时

### funcguard.ip_utils

#### get_local_ip()

- **参数**: 无
- **返回值**: 本机局域网IP地址字符串，如果获取失败返回None
- **功能**: 获取本机局域网IP地址，通过创建UDP socket连接外部地址来获取本机IP

#### get_public_ip()

- **参数**: 无
- **返回值**: 公网IP地址字符串，如果获取失败返回None
- **功能**: 获取本机公网IP地址，使用多个IP查询服务作为备选（ipify.org、ipapi.co、ifconfig.me等），自动验证返回的IP地址格式

#### is_valid_ip(ip_string)

- **参数**:
  - `ip_string`: 要验证的IP地址字符串
- **返回值**: 如果是有效的IP地址返回True，否则返回False
- **功能**: 验证字符串是否为有效的IP地址，检查IP地址格式（4个部分，每部分0-255）

#### get_ip_info()

- **参数**: 无
- **返回值**: 包含IP信息的字典，格式为`{'local_ip': '...', 'public_ip': '...', 'hostname': '...'}`
- **功能**: 获取本机IP地址信息（包括局域网IP、公网IP和主机名）

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

#### print_progress(idx: int, total: int, message: str = "") -> None

- **参数**:
  - `idx`: 当前索引（从0开始）
  - `total`: 总数量
  - `message`: 额外消息，默认为空字符串
- **返回值**: 无
- **功能**: 打印进度条，显示当前进度，设计原理：
  - 进度条总长度固定为50个字符，这是终端显示的最佳长度
  - 使用整除2(//2)将0-100%映射到0-50字符，确保平滑过渡
  - 已完成部分用'█'表示，未完成部分用'-'表示
  - 使用\r回到行首覆盖之前的内容，保持在同一行更新

### funcguard.pd_utils

#### pd_fill_null(df, columns, fill_value)

- **参数**:
  - `df`: pandas DataFrame
  - `columns`: 要填充的列，可以是List[str]或Dict[str, Any]。为列表时，所有列使用相同的fill_value；为字典时，键为列名，值为对应的填充值
  - `fill_value`: 填充值，当columns为列表时使用
- **返回值**: 填充后的DataFrame
- **功能**: 替换DataFrame中指定列的空值为指定值

#### pd_round_columns(df, columns, digits=0)

- **参数**:
  - `df`: pandas DataFrame
  - `columns`: 要进行四舍五入的列名列表
  - `digits`: 保留的小数位数，默认为0
- **返回值**: 四舍五入后的DataFrame
- **功能**: 对DataFrame中指定列进行四舍五入操作

#### pd_convert_columns(df, columns)

- **参数**:
  - `df`: pandas DataFrame
  - `columns`: 要转换类型的字典，键为列名，值为目标数据类型。支持的数据类型：'int', 'float', 'str', 'bool', 'datetime'
- **返回值**: 列类型转换后的DataFrame
- **功能**: 转换DataFrame中指定列的数据类型

#### pd_convert_decimal(df, columns=None, default_type='int')

- **参数**:
  - `df`: pandas DataFrame
  - `columns`: 要处理的列，可以是None、List[str]或Dict[str, str]。为None时检测所有列；为列表时检测指定列并使用default_type转换；为字典时键为列名，值为目标类型('int'或'float')
  - `default_type`: 默认转换类型，'int'或'float'，默认为'int'
- **返回值**: 转换后的DataFrame
- **功能**: 检测DataFrame中是否包含Decimal类型的字段，如果包含则转换为指定的数据类型
- **注意**: 只有object类型的列才可能包含Decimal类型数据

#### pd_load_json(df, columns, empty_to_dict=True)

- **参数**:
  - `df`: pandas DataFrame
  - `columns`: 要转换的列名列表
  - `empty_to_dict`: 是否将空字符串转换为{}，默认为True
- **返回值**: JSON转换后的DataFrame
- **功能**: 对DataFrame中指定的列执行json.loads操作，将JSON字符串转换为Python对象


### funcguard.calculate

#### format_difference(old_value: int | float, new_value: int | float) -> str

- **参数**:
  - `old_value`: 旧值（整数或浮点数）
  - `new_value`: 新值（整数或浮点数）
- **返回值**: 格式化的差异字符串
  - 若差异为0，返回空字符串
  - 若差异为正，返回"+差异值"格式
  - 若差异为负，返回"-差异值"格式
- **功能**: 格式化两个数值之间的差异，常用于显示数值变化


## 许可证

MIT License