# 类型转换

FuncGuard 提供多种类型转换功能，支持列类型转换、Decimal 转换、日期时间转换等。

## convert_columns - 列类型转换

转换 DataFrame 中指定列的数据类型，支持 int、float、str、bool、datetime 类型。该函数具有错误处理机制，当类型转换失败时会保持原类型不变。

```python
from funcguard.pd_utils import convert_columns

# 转换多种类型
df = convert_columns(df, {
    'age': 'int',
    'price': 'float',
    'name': 'str',
    'is_active': 'bool',
    'create_time': 'datetime'
})

# 指定 float 类型的小数位数
df = convert_columns(df, {
    'price': 'float',
    'tax': 'float'
}, decimal_places=2)
```

**支持的数据类型：**
- `int`: 整数类型（Int64Dtype）
- `float`: 浮点数类型（Float64Dtype）
- `str`: 字符串类型（StringDtype）
- `bool`: 布尔类型（BooleanDtype）
- `datetime`: 日期时间类型（datetime64[ns]）

**参数说明：**
- `df`: 输入的 DataFrame
- `columns`: 要转换类型的字典，键为列名，值为目标数据类型
- `decimal_places`: 当转换为 'float' 类型时保留的小数位数，默认为 None 表示不限制

**特性说明：**
- 仅转换 DataFrame 中存在的列，不存在的列会被忽略
- 当类型转换失败时（ValueError 或 TypeError），会保持原类型不变，不会抛出异常
- 对于 datetime 类型转换，使用 `pd.to_datetime(df[column], errors='coerce')`，无效值会转换为 NaT
- 对于 float 类型，如果指定了 `decimal_places`，会在转换后执行四舍五入操作

## convert_numeric_series - Series 数值类型转换

将 Series 转换为数值类型，自动检测应该使用 int 还是 float。如果没有小数则转换为 int64，否则保持 float64。

```python
from funcguard.pd_utils import convert_numeric_series

# 自动检测并转换 Series 类型
series = convert_numeric_series(df['price'])

# 指定小数位数
series = convert_numeric_series(df['price'], decimal_places=2)
```

**参数说明：**
- `series`: 输入的 Series
- `decimal_places`: 当结果为 float 类型时保留的小数位数，默认为 None 表示不限制

## convert_decimal - Decimal 类型转换

检测并转换 DataFrame 中包含 Decimal 类型的字段为指定类型。

```python
from funcguard.pd_utils import convert_decimal
from decimal import Decimal

# 自动检测所有列，发现 Decimal 时转换为 int
df = convert_decimal(df)

# 指定列转换为 float
df = convert_decimal(df, ['salary'], 'float')

# 为不同列指定不同转换类型
df = convert_decimal(df, {
    'salary': 'float',
    'tax': 'int'
})

# 指定小数位数
df = convert_decimal(df, ['salary'], 'float', decimal_places=2)
```

**参数说明：**
- `df`: 输入的 DataFrame
- `columns`: 列名列表、字典或 None（检测所有列）
- `target_type`: 转换类型，支持 'int'、'float'、'auto'，默认为 'int'
- `decimal_places`: 当 target_type 为 'auto' 或 'float' 时保留的小数位数，默认为 None

## convert_str_datetime - 字符串转日期时间

将字符串列转换为 datetime 类型。

```python
from funcguard.pd_utils import convert_str_datetime

# 转换日期字符串列
df = convert_str_datetime(df, ['create_time', 'update_time'])
```

## convert_datetime_str - 日期时间转字符串

将 datetime 列转换为指定格式的字符串。

```python
from funcguard.pd_utils import convert_datetime_str

# 转换为完整日期时间字符串
df = convert_datetime_str(df, ['create_time'])

# 只转换日期部分
df = convert_datetime_str(df, ['create_time'], include_time=False)

# 不包含秒
df = convert_datetime_str(df, ['create_time'], include_seconds=False)
```
