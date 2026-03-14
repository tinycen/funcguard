# FuncGuard Pandas工具包

FuncGuard的pandas工具包提供了丰富的数据处理功能，包括数据填充、类型转换、JSON处理、统计分析等，旨在简化pandas DataFrame的常见操作。

## 功能概览

- **数据填充**：空值填充、NaT时间填充
- **类型转换**：列类型转换、Decimal转换、日期时间转换
- **JSON处理**：JSON字符串解析和转换
- **统计分析**：高性能的条件统计、掩码构建、数据筛选、组合查询
- **数据格式化**：列四舍五入、字符串格式化

## 安装

```bash
pip install funcguard
```

## 快速开始

```python
import pandas as pd
from funcguard.pd_utils import fill_na, convert_columns, round_columns, load_json

# 创建示例数据
df = pd.DataFrame({
    'name': ['张三', '李四', None, '王五'],
    'age': [25.7, 30.2, 28.9, 35.1],
    'salary': [5000.50, 6000.75, 5500.25, 7000.00],
    'config': ['{"timeout": 30}', '{"timeout": 60}', '', '{"timeout": 90}']
})

# 数据填充
df = fill_na(df, {'name': '未知'})

# 类型转换
df = convert_columns(df, {'age': 'int'})

# 四舍五入
df = round_columns(df, ['salary'], 1)

# JSON解析
df = load_json(df, ['config'])
```

## 详细功能

### 数据填充

#### fill_na - 空值填充

替换DataFrame中指定列的空值为指定值。

```python
from funcguard.pd_utils import fill_na

# 使用字典指定不同列的填充值
df = fill_na(df, {'name': '未知', 'age': 0})

# 使用列表统一填充值
df = fill_na(df, ['name', 'age'], '默认值')
```

**参数说明：**
- `df`: 输入的DataFrame
- `columns`: 列名列表或字典（键为列名，值为填充值）
- `fill_value`: 统一填充值，默认为空字符串

#### fill_nat - NaT时间填充

将指定列的NaT（Not a Time）值替换为指定值，特别适用于时间类型的空值处理。

```python
from funcguard.pd_utils import fill_nat

# 填充时间列的NaT值
df = fill_nat(df, ['create_time', 'update_time'], '1970-01-01')

# 批量填充所有时间类型列
df = fill_nat(df, ['create_time'])
```

### 类型转换

#### convert_columns - 列类型转换

转换DataFrame中指定列的数据类型，支持int、float、str、bool、datetime类型。

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

#### convert_decimal - Decimal类型转换

检测并转换DataFrame中包含Decimal类型的字段为指定类型。

```python
from funcguard.pd_utils import convert_decimal
from decimal import Decimal

# 自动检测所有列，发现Decimal时转换为int
df = convert_decimal(df)

# 指定列转换为float
df = convert_decimal(df, ['salary'], 'float')

# 为不同列指定不同转换类型
df = convert_decimal(df, {
    'salary': 'float',
    'tax': 'int'
})
```

#### convert_str_datetime - 字符串转日期时间

将字符串列转换为datetime类型。

```python
from funcguard.pd_utils import convert_str_datetime

# 转换日期字符串列
df = convert_str_datetime(df, ['create_time', 'update_time'])
```

#### convert_datetime_str - 日期时间转字符串

将datetime列转换为指定格式的字符串。

```python
from funcguard.pd_utils import convert_datetime_str

# 转换为完整日期时间字符串
df = convert_datetime_str(df, ['create_time'])

# 只转换日期部分
df = convert_datetime_str(df, ['create_time'], include_time=False)

# 不包含秒
df = convert_datetime_str(df, ['create_time'], include_seconds=False)
```

### 数据格式化

#### round_columns - 列四舍五入

对DataFrame中指定列进行四舍五入操作。

```python
from funcguard.pd_utils import round_columns

# 四舍五入到整数
df = round_columns(df, ['age', 'price'])

# 保留2位小数
df = round_columns(df, ['salary'], 2)
```

### JSON处理

#### load_json - JSON字符串解析

对DataFrame中指定的列执行json.loads操作，将JSON字符串转换为Python对象。

```python
from funcguard.pd_utils import load_json

# 解析JSON字符串列
df = load_json(df, ['config', 'metadata'])

# 空字符串转换为字典
df = load_json(df, ['config'], empty_to_dict=True)
```

### 统计分析

#### DataFrameStatistics - 高性能统计分析类

用于复用pd.Series对象，优化多次统计操作的性能。特别适合需要多次进行条件统计的场景。

```python
from funcguard.pd_utils import DataFrameStatistics

# 创建统计分析器
stats = DataFrameStatistics(df)

# 构建条件掩码
mask = stats.build_single_mask(('age', '>', 25))

# 组合条件统计
count = stats.count([
    ('age', '>', 25),
    ('salary', '>', 5000)
], logic='and')

# 获取DataFrame信息
info = stats.dataframe_info()
```

#### pd_filter - 智能数据筛选

`pd_filter` 是一个智能的数据筛选函数，自动识别条件类型并选择最优的筛选策略，是最推荐使用的筛选方式。
具体实现，是通过调用 `pd_build_mask` 等相关函数，构建掩码，再使用掩码进行筛选。

```python
from funcguard import pd_filter

# 单个条件筛选
filtered_df = pd_filter(df, ('age', '>', 25))

# 多个条件 AND 筛选
filtered_df = pd_filter(df, [
    ('age', '>', 25),
    ('salary', '>', 5000),
    ('is_active', '==', True)
], logic='and')

# 多个条件 OR 筛选
filtered_df = pd_filter(df, [
    ('dept', '==', 'IT'),
    ('dept', '==', 'HR'),
    ('level', '>=', 3)
], logic='or')

# 空值判断
filtered_df = pd_filter(df, ('email', 'null'))
filtered_df = pd_filter(df, ('phone', 'not null'))

# 字符串匹配
filtered_df = pd_filter(df, ('name', 'contains', '张'))
filtered_df = pd_filter(df, ('email', 'startswith', 'admin'))
filtered_df = pd_filter(df, ('file', 'endswith', '.pdf'))

# 复杂逻辑组合：先分别筛选，再组合结果
# 场景：筛选 (年龄>25 且 工资>5000) 或 (部门是IT 且 级别>=3)
group1 = pd_filter(df, [
    ('age', '>', 25),
    ('salary', '>', 5000)
], logic='and')

group2 = pd_filter(df, [
    ('dept', '==', 'IT'),
    ('level', '>=', 3)
], logic='and')

# 合并两个结果（去重）
filtered_df = pd.concat([group1, group2]).drop_duplicates()
```

**智能识别条件类型：**
- 单个条件元组 `('age', '>', 25)`：使用性能最优的单条件筛选
- 条件元组列表 `[('age', '>', 25), ...]`：使用多条件组合筛选
- 掩码Series列表 `[mask1, mask2]`：使用掩码组合筛选

#### 掩码构建函数

如果需要更底层的控制，可以直接使用掩码构建函数。这些函数返回布尔掩码而不是筛选后的DataFrame。

掩码构建函数提供了灵活的数据筛选能力，支持从 `funcguard` 直接导入使用。

##### pd_build_mask - 单个条件掩码

构建单个条件的掩码，性能最优，无额外内存分配。

```python
from funcguard import pd_build_mask

# 基本比较运算
mask = pd_build_mask(df, ('age', '>', 25))
mask = pd_build_mask(df, ('salary', '>=', 5000))
mask = pd_build_mask(df, ('name', '==', '张三'))

# 集合运算
mask = pd_build_mask(df, ('dept', 'in', ['IT', 'HR', 'Finance']))
mask = pd_build_mask(df, ('status', 'not in', ['deleted', 'inactive']))

# 空值判断
mask = pd_build_mask(df, ('email', 'null'))
mask = pd_build_mask(df, ('phone', 'not null'))

# 字符串匹配
mask = pd_build_mask(df, ('name', 'contains', '张'))
mask = pd_build_mask(df, ('email', 'startswith', 'admin'))
mask = pd_build_mask(df, ('file', 'endswith', '.pdf'))

# 应用掩码筛选数据
filtered_df = df[mask]
```

##### pd_build_masks - 多个条件掩码

构建多个条件的组合掩码，支持 `and` 和 `or` 逻辑。

```python
from funcguard import pd_build_masks

# AND 逻辑：所有条件同时满足
mask = pd_build_masks(df, [
    ('age', '>', 25),
    ('salary', '>', 5000),
    ('is_active', '==', True)
], logic='and')

# OR 逻辑：任一条件满足
mask = pd_build_masks(df, [
    ('dept', '==', 'IT'),
    ('dept', '==', 'HR'),
    ('level', '>=', 3)
], logic='or')

# 应用掩码
filtered_df = df[mask]
```

##### pd_combine_masks - 掩码组合

组合多个已构建的掩码，支持复杂的嵌套逻辑组合。

```python
from funcguard import pd_build_mask, pd_build_masks, pd_combine_masks

# 场景：筛选 (年龄>25 且 工资>5000) 或 (部门是IT 且 级别>=3)

# 构建基础掩码
mask1 = pd_build_masks(df, [
    ('age', '>', 25),
    ('salary', '>', 5000)
], logic='and')

mask2 = pd_build_masks(df, [
    ('dept', '==', 'IT'),
    ('level', '>=', 3)
], logic='and')

# 组合掩码（OR逻辑）
combined_mask = pd_combine_masks([mask1, mask2], logic='or')

# 更复杂的组合：(A AND B) OR (C AND D) OR E
mask_a = pd_build_mask(df, ('age', '>', 30))
mask_b = pd_build_mask(df, ('salary', '>', 8000))
mask_c = pd_build_mask(df, ('dept', 'in', ['IT', 'RD']))
mask_d = pd_build_mask(df, ('level', '>=', 5))
mask_e = pd_build_mask(df, ('is_vip', '==', True))

group1 = pd_combine_masks([mask_a, mask_b], logic='and')
group2 = pd_combine_masks([mask_c, mask_d], logic='and')
final_mask = pd_combine_masks([group1, group2, mask_e], logic='or')

filtered_df = df[final_mask]
```

##### pd_count - 条件统计

统计符合条件的非空值数量。

```python
from funcguard.pd_utils import pd_count

# 单个条件
count = pd_count(df, ('age', '>', 25))

# 多个条件
count = pd_count(df, [
    ('age', '>', 25),
    ('salary', '>', 5000)
], logic='and')
```

## 支持的运算符

在条件查询中支持以下运算符：
- `==`: 等于
- `!=`: 不等于
- `>`: 大于
- `>=`: 大于等于
- `<`: 小于
- `<=`: 小于等于
- `in`: 包含在列表中
- `not in`: 不包含在列表中
- `null`: 为空
- `not null`: 不为空
- `startswith`: 以指定字符串开头
- `endswith`: 以指定字符串结尾
- `contains`: 包含字符串
- `not contains`: 不包含字符串


## 性能优化

DataFrameStatistics类通过以下方式优化性能：
1. **缓存基础掩码**：避免重复创建pd.Series([True] * len(df))
2. **复用DataFrame索引**：减少内存分配
3. **批量统计功能**：减少函数调用开销
4. **原生pandas表达式**：简单条件直接使用原生表达式，无额外内存分配

## 完整示例

```python
import pandas as pd
from funcguard.pd_utils import (
    fill_na, fill_nat, convert_columns, convert_decimal,
    round_columns, load_json, DataFrameStatistics
)

# 创建示例数据
df = pd.DataFrame({
    'name': ['张三', '李四', None, '王五', '赵六'],
    'age': [25.7, 30.2, 28.9, 35.1, 42.5],
    'salary': [5000.50, 6000.75, 5500.25, 7000.00, 8000.00],
    'join_date': ['2023-01-15', '2023-02-20', None, '2023-04-05', '2023-05-10'],
    'config': ['{"dept": "IT"}', '{"dept": "HR"}', '', '{"dept": "Finance"}', '{"dept": "Sales"}'],
    'is_active': [True, True, False, True, False]
})

print("原始数据:")
print(df)
print("\n数据类型:")
print(df.dtypes)

# 数据清洗和转换
print("\n=== 数据清洗和转换 ===")

# 1. 填充空值
df = fill_na(df, {'name': '未知'})

# 2. 转换数据类型
df = convert_columns(df, {
    'age': 'int',
    'join_date': 'datetime',
    'is_active': 'bool'
})

# 3. 四舍五入工资
df = round_columns(df, ['salary'], 0)

# 4. 解析JSON配置
df = load_json(df, ['config'])

print("\n处理后的数据:")
print(df)
print("\n处理后的数据类型:")
print(df.dtypes)

# 数据筛选
print("\n=== 数据筛选 ===")

# 筛选年龄大于30岁的员工
filtered_df = pd_filter(df, ('age', '>', 30))
print(f"年龄大于30岁的员工:\n{filtered_df[['name', 'age']]}")

# 筛选IT部门且活跃的员工
it_active_df = pd_filter(df, [
    ('config', 'contains', 'IT'),
    ('is_active', '==', True)
], logic='and')
print(f"\nIT部门且活跃的员工:\n{it_active_df[['name', 'dept']]}")

# 统计分析
print("\n=== 统计分析 ===")
stats = DataFrameStatistics(df)

# 统计年龄大于30岁的员工数量
age_count = stats.count(('age', '>', 30))
print(f"年龄大于30岁的员工数量: {age_count}")

# 统计IT部门且活跃的员工数量
it_active_count = stats.count([
    ('config', 'contains', 'IT'),
    ('is_active', '==', True)
], logic='and')
print(f"IT部门且活跃的员工数量: {it_active_count}")

# 获取DataFrame信息
info = stats.dataframe_info()
print(f"DataFrame形状: {info['shape']}")
print(f"列名: {info['columns']}")
```
