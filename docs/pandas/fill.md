# 数据填充

FuncGuard 提供数据填充功能，用于处理 DataFrame 中的空值。

## fill_na - 空值填充

替换 DataFrame 中指定列的空值为指定值。

```python
from funcguard.pd_utils import fill_na

# 使用字典指定不同列的填充值
df = fill_na(df, {'name': '未知', 'age': 0})

# 使用列表统一填充值
df = fill_na(df, ['name', 'age'], '默认值')
```

**参数说明：**
- `df`: 输入的 DataFrame
- `columns`: 列名列表或字典（键为列名，值为填充值）
- `fill_value`: 统一填充值，默认为空字符串

## fill_nat - NaT 时间填充

将指定列的 NaT（Not a Time）值替换为指定值，特别适用于时间类型的空值处理。

```python
from funcguard.pd_utils import fill_nat

# 填充时间列的 NaT 值
df = fill_nat(df, ['create_time', 'update_time'], '1970-01-01')

# 批量填充所有时间类型列
df = fill_nat(df, ['create_time'])
```

## cal_date_diff - 日期差值计算填充

计算 DataFrame 中两列日期的时间差，并将结果填充到指定列。支持自动将字符串类型日期转换为 datetime 类型。

```python
from funcguard.pd_utils import cal_date_diff

# 计算两列日期的小时差，结果填充到 duration 列
df = cal_date_diff(df, target_column='duration', old_date_column='start_time', new_date_column='end_time')

# 计算天数差，保留 2 位小数
df = cal_date_diff(df, target_column='days_diff', old_date_column='create_time', new_date_column='update_time', unit='day', decimal_places=2)
```

**参数说明：**
- `df`: 输入的 DataFrame
- `target_column`: 要填充计算结果的列名
- `old_date_column`: 原始日期列名
- `new_date_column`: 新日期列名
- `unit`: 返回单位，`"h"` 返回小时数，`"day"` 返回天数，默认为 `"h"`
- `decimal_places`: 保留的小数位数，默认为 1
