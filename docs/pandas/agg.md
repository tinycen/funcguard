# 分组聚合统计

FuncGuard 提供分组聚合统计功能，用于按指定列分组后对另一列进行聚合计算（求和、平均值等）。

## 函数列表

| 函数名 | 说明 |
|--------|------|
| `pd_group_agg` | 按指定列分组，对另一列进行聚合统计 |

## pd_group_agg - 分组聚合

按指定列分组，对另一列进行聚合统计（求和、平均值等）。

```python
from funcguard.pd_utils import pd_group_agg

# 基本用法：按 category 分组，对 amount 列求和
result = pd_group_agg(df, "category", "amount", "sum")
# {'A': 1000, 'B': 2000, 'C': 1500}

# 求平均值
result = pd_group_agg(df, "category", "amount", "mean")
# {'A': 100.0, 'B': 200.0, 'C': 150.0}

# 求最大值
result = pd_group_agg(df, "category", "amount", "max")
# {'A': 500, 'B': 800, 'C': 600}

# 求最小值
result = pd_group_agg(df, "category", "amount", "min")
# {'A': 100, 'B': 200, 'C': 150}

# 计数
result = pd_group_agg(df, "category", "amount", "count")
# {'A': 10, 'B': 15, 'C': 12}

# 降序排序（值大的在前）
result = pd_group_agg(df, "category", "amount", "sum", sort="desc")
# {'B': 2000, 'C': 1500, 'A': 1000}

# 升序排序（值小的在前）
result = pd_group_agg(df, "category", "amount", "sum", sort="asc")
# {'A': 1000, 'C': 1500, 'B': 2000}

# 带条件过滤统计
result = pd_group_agg(df, "category", "amount", "sum", conditions=[("status", "==", "active")])
# 只统计 status == active 的记录

# 组合条件过滤
result = pd_group_agg(
    df,
    "category",
    "amount",
    "sum",
    sort="desc",
    conditions=[
        ("status", "==", "active"),
        ("region", "==", "north")
    ],
    logic="and"
)

# 返回 DataFrame 格式
result = pd_group_agg(df, "category", "amount", "sum", return_type="df")
#        amount
# category
# A        1000
# B        2000
# C        1500

# 返回 Series 格式
result = pd_group_agg(df, "category", "amount", "sum", return_type="series")
# category
# A    1000
# B    2000
# C    1500
# Name: amount, dtype: int64
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `df` | `pd.DataFrame` | 必填 | 输入的 DataFrame |
| `group_col` | `str` | 必填 | 分组列名 |
| `agg_col` | `str` | 必填 | 聚合列名 |
| `agg_func` | `str` | `"sum"` | 聚合函数：`"sum"` / `"mean"` / `"max"` / `"min"` / `"count"` / `"median"` / `"std"` / `"var"` |
| `sort` | `Optional[str]` | `None` | 排序方式：`"asc"` 升序 / `"desc"` 降序 / `None` 不排序 |
| `conditions` | `Optional[list]` | `None` | 可选的过滤条件 |
| `logic` | `str` | `"and"` | 多条件逻辑：`"and"` / `"or"` |
| `return_type` | `str` | `"dict"` | 返回类型：`"dict"`（字典）/ `"df"`（DataFrame）/ `"series"`（Series）|

### 支持的聚合函数

| 聚合函数 | 说明 |
|----------|------|
| `sum` | 求和 |
| `mean` | 平均值 |
| `max` | 最大值 |
| `min` | 最小值 |
| `count` | 计数 |
| `median` | 中位数 |
| `std` | 标准差 |
| `var` | 方差 |
