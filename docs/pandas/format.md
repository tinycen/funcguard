# 数据格式化

FuncGuard 提供数据格式化功能，用于对 DataFrame 中的数据进行格式化操作。

## round_columns - 列四舍五入

对 DataFrame 中指定列进行四舍五入操作。

```python
from funcguard.pd_utils import round_columns

# 四舍五入到整数
df = round_columns(df, ['age', 'price'])

# 保留 2 位小数
df = round_columns(df, ['salary'], 2)
```
