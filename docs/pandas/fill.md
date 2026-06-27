# 数据填充

FuncGuard 提供数据填充功能，用于处理 DataFrame 中的空值。

## fill_na - 空值填充

替换 DataFrame 中指定列的空值为指定值。支持数值类型自动转换和精度控制，对日期时间类型有特殊处理避免转换错误。

```python
from funcguard.pd_utils import fill_na

# 使用字典指定不同列的填充值
df = fill_na(df, {'name': '未知', 'age': 0})

# 使用列表统一填充值
df = fill_na(df, ['name', 'age'], '默认值')

# 数值填充并指定小数位数
df = fill_na(df, ['price', 'discount'], 0.0, decimal_places=2)

# 空列表填充所有列
df = fill_na(df, [], '默认值')  # 对所有列填充 '默认值'
df = fill_na(df, [], 0.0, decimal_places=2)  # 对所有列填充 0.0 并保留 2 位小数
```

**参数说明：**
- `df`: 输入的 DataFrame
- `columns`: 列名列表或字典（键为列名，值为填充值），传入空列表时对所有列应用填充
- `fill_value`: 统一填充值，默认为空字符串
- `decimal_places`: 数值转换时保留的小数位数，默认为 None 表示不限制

