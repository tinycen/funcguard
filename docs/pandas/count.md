# 条件计数统计

FuncGuard 提供高性能的条件计数统计功能，用于统计 DataFrame 中符合条件的记录数量。

## 函数列表

| 函数名 | 说明 |
|--------|------|
| `pd_count` | 统计符合条件的记录数 |
| `pd_value_counts` | 统计指定列中不同值的计数/百分比 |

## pd_count - 条件计数

统计 DataFrame 中符合条件的非空值数量。

```python
from funcguard.pd_utils import pd_count

# 基本用法：统计年龄大于 25 岁的记录数
count = pd_count(df, ('age', '>', 25))

# 多条件统计（and 逻辑）
count = pd_count(df, [
    ('age', '>', 25),
    ('salary', '>', 5000)
], logic='and')

# 多条件统计（or 逻辑）
count = pd_count(df, [
    ('department', '==', 'IT'),
    ('department', '==', 'HR')
], logic='or')
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `df` | `pd.DataFrame` | 必填 | 输入的 DataFrame |
| `conditions` | `Union[Tuple, List[Tuple]]` | 必填 | 条件表达式或条件列表 |
| `logic` | `str` | `"and"` | 多条件逻辑：`"and"` / `"or"` |

## pd_value_counts - 不同值计数统计

统计指定列中不同值的计数数据，支持计数模式和百分比模式。

```python
from funcguard.pd_utils import pd_value_counts

# 基本用法：统计各状态的数量
result = pd_value_counts(df, "status")
# {'active': 150, 'inactive': 50, 'pending': 20}

# 百分比模式
result = pd_value_counts(df, "status", mode="percent")
# {'active': 0.6818, 'inactive': 0.2273, 'pending': 0.0909}

# 降序排序（数量多的在前）
result = pd_value_counts(df, "status", sort="desc")

# 升序排序（数量少的在前）
result = pd_value_counts(df, "status", sort="asc")

# 带条件过滤统计
result = pd_value_counts(df, "status", conditions=[("age", ">", 18)])
# 只统计 age > 18 的记录中各状态的数量

# 组合条件过滤
result = pd_value_counts(
    df,
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

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `df` | `pd.DataFrame` | 必填 | 输入的 DataFrame |
| `column` | `str` | 必填 | 要统计的列名 |
| `mode` | `str` | `"count"` | 统计模式：`"count"` 计数 / `"percent"` 百分比 |
| `sort` | `Optional[str]` | `None` | 排序方式：`"asc"` 升序 / `"desc"` 降序 / `None` 不排序 |
| `dropna` | `bool` | `True` | 是否排除空值 |
| `conditions` | `Optional[list]` | `None` | 可选的过滤条件 |
| `logic` | `str` | `"and"` | 多条件逻辑：`"and"` / `"or"` |
