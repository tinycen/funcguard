# 日期时间工具

FuncGuard 提供专门的日期时间处理功能，用于处理 DataFrame 中的日期时间数据。

## fill_nat - NaT 时间填充

将指定列的 NaT（Not a Time）值替换为指定值，特别适用于时间类型的空值处理。支持datetime和timedelta类型，默认填充为空字符串。

```python
from funcguard.pd_utils import fill_nat

# 单个填充 时间列的 NaT 值为空字符串（默认行为）
df = fill_nat(df, 'create_time')

# 批量填充 多个时间列的 NaT 值为空字符串
df = fill_nat(df, ['create_time', 'update_time'])

# 填充时间列的 NaT 值为指定日期字符串
df = fill_nat(df, 'log_time', fill_value='2000-01-01 00:00:00')
df = fill_nat(df, ['create_time', 'update_time'], fill_value='1970-01-01')
```

**参数说明：**
- `df`: 输入的 DataFrame
- `columns`: 列名列表或字符串
- `fill_value`: 填充值，默认为空字符串

## cal_date_diff - 日期差值计算填充

计算 DataFrame 中两列日期的时间差（或一列日期与指定日期时间的差值），并将结果填充到指定列。支持自动将字符串类型日期转换为 datetime 类型。

```python
from funcguard.pd_utils import cal_date_diff
from funcguard.time_utils import get_now

# 计算两列日期的小时差，结果填充到 duration 列
df = cal_date_diff(df, target_column='duration', old_date='start_time', new_date='end_time')

# 计算天数差，保留 2 位小数
df = cal_date_diff(df, target_column='days_diff', old_date='create_time', new_date='update_time', unit='d', decimal_places=2)

# 使用 datetime 对象作为新日期（例如计算到当前时间的差值）
df = cal_date_diff(df, target_column='hours_since_create', old_date='create_time', new_date=get_now())

# 当日期存在空值时，使用指定值填充计算结果
df = cal_date_diff(df, target_column='duration', old_date='start_time', new_date='end_time', nat=-1)
```

**参数说明：**
- `df`: 输入的 DataFrame
- `target_column`: 要填充计算结果的列名
- `old_date`: 原始日期，可以是列名字符串（`str`）或 `datetime` 对象
- `new_date`: 新日期，可以是列名字符串（`str`）或 `datetime` 对象
- `unit`: 返回单位，`"h"` 返回小时数，`"d"` 返回天数，`"m"` 返回分钟数，`"s"` 返回秒数，默认为 `"h"`
- `decimal_places`: 保留的小数位数，默认为 1
- `nat`: 当日期为 NaT 时的填充值，默认为 `None` 表示不特殊处理

**支持的单位：**
- `"s"`: 秒
- `"m"`: 分钟
- `"h"`: 小时（默认）
- `"d"`: 天

## 使用示例

```python
import pandas as pd
from funcguard.pd_utils import fill_nat, cal_date_diff
from datetime import datetime

# 创建示例数据
df = pd.DataFrame({
    'order_id': [1, 2, 3, 4, 5],
    'create_time': ['2023-01-15 10:30:00', '2023-02-20 14:15:00', None, '2023-04-05 09:45:00', '2023-05-10 16:20:00'],
    'pay_time': ['2023-01-15 11:00:00', None, '2023-03-15 20:30:00', '2023-04-05 10:15:00', None],
    'ship_time': [None, '2023-02-21 08:00:00', '2023-03-16 14:20:00', None, '2023-05-12 11:30:00']
})

# 转换时间列为 datetime 类型
df['create_time'] = pd.to_datetime(df['create_time'])
df['pay_time'] = pd.to_datetime(df['pay_time'])
df['ship_time'] = pd.to_datetime(df['ship_time'])

print("原始数据:")
print(df)

# 处理 NaT 值
print("\n=== 处理 NaT 值 ===")

# 将时间列的 NaT 值替换为指定字符串
df = fill_nat(df, ['create_time', 'pay_time', 'ship_time'], fill_value='未记录')
print("\n填充 NaT 后的数据:")
print(df)

# 计算时间差
print("\n=== 计算时间差 ===")

# 计算支付时长（小时）
df = cal_date_diff(df, target_column='pay_duration', old_date='create_time', new_date='pay_time', unit='h', decimal_places=1)

# 计算发货时长（天）
df = cal_date_diff(df, target_column='ship_days', old_date='pay_time', new_date='ship_time', unit='d', decimal_places=2)

# 计算到当前时间的总时长（小时）
current_time = datetime.now()
df = cal_date_diff(df, target_column='total_hours', old_date='create_time', new_date=current_time, unit='h', decimal_places=1)

print("\n计算时间差后的数据:")
print(df[['order_id', 'pay_duration', 'ship_days', 'total_hours']])

# 处理包含空值的时间差计算
print("\n=== 处理包含空值的时间差计算 ===")

# 当存在 NaT 时，使用指定值填充计算结果
df_with_nat = pd.DataFrame({
    'order_id': [1, 2, 3],
    'start_time': ['2023-01-01 10:00:00', None, '2023-01-03 15:00:00'],
    'end_time': ['2023-01-01 12:30:00', '2023-01-02 16:45:00', None]
})

df_with_nat['start_time'] = pd.to_datetime(df_with_nat['start_time'])
df_with_nat['end_time'] = pd.to_datetime(df_with_nat['end_time'])

# 使用 nat 参数处理空值
df_with_nat = cal_date_diff(
    df_with_nat, 
    target_column='duration_hours', 
    old_date='start_time', 
    new_date='end_time', 
    unit='h', 
    nat=-999
)

print("\n处理空值后的时间差:")
print(df_with_nat)
```