# 类型转换

FuncGuard 提供多种类型转换功能，支持列类型转换、Decimal 转换、日期时间转换等。

## convert_columns - 列类型转换

转换 DataFrame 中指定列的数据类型，支持 int、float、str、bool、datetime 类型。

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
```

**支持的数据类型：**
- `int`: 整数类型（Int64Dtype）
- `float`: 浮点数类型（Float64Dtype）
- `str`: 字符串类型（StringDtype）
- `bool`: 布尔类型（BooleanDtype）
- `datetime`: 日期时间类型（datetime64[ns]）

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
```

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
