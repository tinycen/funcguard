# 时间工具

FuncGuard 提供时间工具功能，用于时间计算、日志记录和执行时间监控。

## time_log - 打印带时间戳的日志

打印带时间戳的日志信息，支持进度显示和预计完成时间。

```python
from funcguard import time_log
from datetime import datetime, timezone, timedelta

# 基本使用
s_time = datetime.now(timezone(timedelta(hours=8)))
for i in range(100):
    time_log("处理中", i=i, max_num=100, s_time=s_time)

# 使用日志级别
from funcguard import time_log
time_log("开始处理", level="INFO")
time_log("处理完成", level="SUCCESS")
```

**参数说明：**
- `message`: 日志消息
- `i`: 当前进度
- `max_num`: 总进度数量
- `s_time`: 开始时间，用于计算预计完成时间
- `start_from`: i是否从0开始，`0`表示从0开始，`1`表示从1开始
- `return_field`: 返回字段，支持 `"progress_info"` 表示完整进度信息，`"remaining_time"` 表示剩余时间，`"end_time"` 表示预计完成时间
- `level`: 日志等级，支持 `DEBUG`/`INFO`/`PROGRESS`/`SUCCESS`/`WARNING`/`WARN`/`ERROR`/`CRITICAL`/`FATAL`，为空时仅 print

**返回值：**
- 根据 `return_field` 参数返回不同的信息

---

## time_diff - 计算持续时间

计算并打印任务执行时间统计信息。

```python
from funcguard import time_diff
from datetime import datetime, timezone, timedelta

# 获取开始时间
s_time = time_diff()  # 返回当前时间

# 执行任务...
import time
time.sleep(2)

# 计算耗时
time_diff(s_time)  # 打印总耗时

# 计算多个任务的平均耗时
time_diff(s_time, max_num=10)

# 英文输出
time_diff(s_time, language="en")

# 返回秒数不打印
total_seconds = time_diff(s_time, return_duration=0)

# 打印并返回秒数
total_seconds = time_diff(s_time, return_duration=2)
```

**参数说明：**
- `s_time`: 开始时间，如果为 `None` 则返回当前时间
- `max_num`: 任务数量，大于0时会计算平均耗时
- `language`: 语言选择，`"cn"` 中文，其他为英文
- `return_duration`: 返回模式
  - `0`: 仅返回 `total_seconds`，不打印信息
  - `1`: 仅打印信息，不返回 `total_seconds`
  - `2`: print 信息，并返回 `total_seconds`

**返回值：**
- 如果 `s_time` 为 `None` 则返回当前时间
- 根据 `return_duration` 返回 `total_seconds` 或不返回

---

## time_monitor - 监控函数执行时间

监控函数执行时间，并返回函数的执行结果和执行时间。

```python
from funcguard import time_monitor
import time

def my_function(a, b):
    time.sleep(1)
    return a + b

# 基本使用
result = time_monitor(func=my_function, 1, 2)

# 设置警告阈值（超过则打印警告）
result = time_monitor(warning_threshold=0.5, func=my_function, 1, 2)

# 总是打印执行时间
result = time_monitor(print_mode=1, func=my_function, 1, 2)

# 仅返回结果和耗时，不打印
result, seconds = time_monitor(print_mode=0, func=my_function, 1, 2)
```

**参数说明：**
- `warning_threshold`: 警告阈值（秒），如果执行耗时超过此值则打印警告
- `print_mode`: 打印模式
  - `0`: 仅返回 `total_seconds`，不打印任何信息，返回 `(result, total_seconds)`
  - `1`: 总是打印执行时间
  - `2`: 仅在超时打印警告信息（默认）
- `func`: 要监控的函数
- `*args`: 函数的位置参数
- `**kwargs`: 函数的关键字参数

**返回值：**
- `print_mode == 0`: `(函数的执行结果, total_seconds)`
- `print_mode == 1` 或 `2`: 函数的执行结果

---

## get_now - 获取当前时间

获取当前时间，支持多种时区。

```python
from funcguard import get_now

# 获取本地时间（不含时区信息）
now = get_now(from_timezone="local")

# 获取UTC时间（含时区信息）
now = get_now(from_timezone="utc", remove_tzinfo=False)

# 获取北京时间（含时区信息）
now = get_now(from_timezone="beijing", remove_tzinfo=False)
```

**参数说明：**
- `from_timezone`: 时区选择
  - `"local"`: 本地时间（tz-naive，不含时区信息）
  - `"utc"`: UTC时间（tz-aware，包含UTC时区信息）
  - `"beijing"`: 北京时间（tz-aware，包含UTC+8时区信息）
- `remove_tzinfo`: 是否移除时区信息，默认为 `True`

**返回值：**
- `datetime` 对象

---

## generate_timestamp - 获取时间戳

获取当前时间戳或格式化时间字符串。

```python
from funcguard import generate_timestamp

# 获取毫秒级时间戳（默认）
ts = generate_timestamp()  # 例如：1710504000000

# 获取ISO 8601格式时间
iso_time = generate_timestamp(fmt="iso")  # 例如：2024-03-15T14:00:00

# 获取UTC时间并带Z标志
utc_iso = generate_timestamp(from_timezone="utc", fmt="iso", utc_z=True)  # 例如：2024-03-15T06:00:00Z

# 获取格式化字符串
str_time = generate_timestamp(fmt="str")  # 例如：2024-03-15 14:00:00
```

**参数说明：**
- `from_timezone`: 时区选择
  - `"local"`: 本地时间的 naive 对象（不含时区信息）
  - `"utc"`: UTC时间的 aware 对象（包含UTC时区信息）
  - `"beijing"`: 北京时间的 aware 对象（包含UTC+8时区信息）
- `fmt`: 格式选择
  - `"millis"`: 毫秒级时间戳（默认）
  - `"iso"`: ISO 8601标准格式
  - `"str"`: 字符串格式 `%Y-%m-%d %H:%M:%S`
- `utc_z`: 是否在UTC的iso格式后追加Z标志，仅在 `fmt="iso"` 且时区为UTC时有效

**返回值：**
- 根据 `fmt` 返回对应值（`int` 或 `str`）

---

## cal_date_diff - 计算日期差值

计算两个日期的差值，返回小时数或天数。

```python
from funcguard import cal_date_diff
from datetime import datetime

# 计算两个日期的小时差
old_date = datetime(2024, 1, 1, 12, 0, 0)
new_date = datetime(2024, 1, 2, 14, 30, 0)
hours = cal_date_diff(old_date, new_date)  # 返回 26.5

# 计算天数差，保留 2 位小数
days = cal_date_diff(old_date, new_date, unit='day', decimal_places=2)  # 返回 1.10
```

**参数说明：**
- `old_date`: 原始日期 (datetime 类型)
- `new_date`: 新日期 (datetime 类型)
- `unit`: 返回单位，`"h"` 返回小时数，`"day"` 返回天数，默认为 `"h"`
- `decimal_places`: 保留的小数位数，默认为 1

**返回值：**
- `int | float`: 日期差值

---

## time_wait - 时间等待

等待指定的秒数，显示倒计时。

```python
from funcguard import time_wait

# 等待10秒（默认）
time_wait()

# 等待5秒
time_wait(5)
```

**参数说明：**
- `seconds`: 等待的秒数，默认值为 10 秒

**返回值：**
- 无
