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
