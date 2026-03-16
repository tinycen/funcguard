# FuncGuard Pandas 工具包

FuncGuard 的 pandas 工具包提供了丰富的数据处理功能，包括数据填充、类型转换、JSON 处理、统计分析等，旨在简化 pandas DataFrame 的常见操作。

## 功能清单

| 功能模块 | 说明 | 详细文档 |
|----------|------|----------|
| **数据填充** | 空值填充、NaT 时间填充、日期差值计算填充 | [fill.md](./pandas/fill.md) |
| **类型转换** | 列类型转换、Series 数值转换、Decimal 转换、日期时间转换 | [convert.md](./pandas/convert.md) |
| **数据格式化** | 列四舍五入、字符串格式化 | [format.md](./pandas/format.md) |
| **JSON 处理** | JSON 字符串解析和转换 | [json.md](./pandas/json.md) |
| **数据筛选** | 智能条件筛选 | [filter.md](./pandas/filter.md) |
| **掩码构建** | 底层掩码构建函数 | [mask.md](./pandas/mask.md) |
| **统计分析** | 高性能的条件统计、数据筛选 | [statistics.md](./pandas/statistics.md) |
| **运算符** | 条件查询支持的运算符列表 | [operators.md](./pandas/operators.md) |

## 安装

```bash
pip install funcguard
```

## 快速开始

```python
import pandas as pd
from funcguard.pd_utils import fill_na, convert_columns, round_columns, load_json
from funcguard import pd_filter, pd_convert_numeric_series

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

# Series 数值类型转换（自动检测 int/float）
df['salary'] = pd_convert_numeric_series(df['salary'], decimal_places=2)

# 四舍五入
df = round_columns(df, ['salary'], 1)

# JSON 解析
df = load_json(df, ['config'])

# 数据筛选
filtered_df = pd_filter(df, ('age', '>', 30))
```

## 完整示例

```python
import pandas as pd
from funcguard.pd_utils import (
    fill_na, fill_nat, convert_columns, convert_decimal,
    round_columns, load_json, DataFrameStatistics
)
from funcguard import pd_filter

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

# 4. 解析 JSON 配置
df = load_json(df, ['config'])

print("\n处理后的数据:")
print(df)
print("\n处理后的数据类型:")
print(df.dtypes)

# 数据筛选
print("\n=== 数据筛选 ===")

# 筛选年龄大于 30 岁的员工
filtered_df = pd_filter(df, ('age', '>', 30))
print(f"年龄大于 30 岁的员工:\n{filtered_df[['name', 'age']]}")

# 筛选 IT 部门且活跃的员工
it_active_df = pd_filter(df, [
    ('config', 'contains', 'IT'),
    ('is_active', '==', True)
], logic='and')
print(f"\nIT 部门且活跃的员工:\n{it_active_df[['name']]}")

# 统计分析
print("\n=== 统计分析 ===")
stats = DataFrameStatistics(df)

# 统计年龄大于 30 岁的员工数量
age_count = stats.count(('age', '>', 30))
print(f"年龄大于 30 岁的员工数量: {age_count}")

# 统计 IT 部门且活跃的员工数量
it_active_count = stats.count([
    ('config', 'contains', 'IT'),
    ('is_active', '==', True)
], logic='and')
print(f"IT 部门且活跃的员工数量: {it_active_count}")

# 获取 DataFrame 信息
info = stats.dataframe_info()
print(f"DataFrame 形状: {info['shape']}")
print(f"列名: {info['columns']}")
```
