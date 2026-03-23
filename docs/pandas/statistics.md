# 统计分析

FuncGuard 提供高性能的统计分析功能，用于复用 pd.Series 对象，优化多次统计操作的性能。

## DataFrameStatistics - 高性能统计分析类

用于复用 pd.Series 对象，优化多次统计操作的性能。特别适合需要多次进行条件统计的场景。

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

# 获取 DataFrame 信息
info = stats.dataframe_info()
```

### value_counts - 不同值计数统计

统计指定列中不同值的计数数据，支持计数模式和百分比模式。

```python
from funcguard.pd_utils import DataFrameStatistics

stats = DataFrameStatistics(df)

# 基本用法：统计各状态的数量
result = stats.value_counts("status")
# {'active': 150, 'inactive': 50, 'pending': 20}

# 百分比模式
result = stats.value_counts("status", mode="percent")
# {'active': 0.6818, 'inactive': 0.2273, 'pending': 0.0909}

# 降序排序（数量多的在前）
result = stats.value_counts("status", sort="desc")

# 升序排序（数量少的在前）
result = stats.value_counts("status", sort="asc")

# 带条件过滤统计
result = stats.value_counts("status", conditions=[("age", ">", 18)])
# 只统计 age > 18 的记录中各状态的数量

# 组合条件过滤
result = stats.value_counts(
    "status",
    mode="percent",
    sort="desc",
    conditions=[
        ("age", ">", 18),
        ("city", "==", "Beijing")
    ],
    logic="and"
)
```

#### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `column` | `str` | 必填 | 要统计的列名 |
| `mode` | `str` | `"count"` | 统计模式：`"count"` 计数 / `"percent"` 百分比 |
| `sort` | `Optional[str]` | `None` | 排序方式：`"asc"` 升序 / `"desc"` 降序 / `None` 不排序 |
| `dropna` | `bool` | `True` | 是否排除空值 |
| `conditions` | `Optional[list]` | `None` | 可选的过滤条件 |
| `logic` | `str` | `"and"` | 多条件逻辑：`"and"` / `"or"` |

## 性能优化

DataFrameStatistics 类通过以下方式优化性能：
1. **缓存基础掩码**：避免重复创建 pd.Series([True] * len(df))
2. **复用 DataFrame 索引**：减少内存分配
3. **批量统计功能**：减少函数调用开销
4. **原生 pandas 表达式**：简单条件直接使用原生表达式，无额外内存分配
