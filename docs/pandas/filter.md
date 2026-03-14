# 数据筛选

FuncGuard 提供智能数据筛选功能，支持条件筛选、掩码构建等操作。

## pd_filter - 智能数据筛选

`pd_filter` 是一个智能的数据筛选函数，自动识别条件类型并选择最优的筛选策略，是最推荐使用的筛选方式。

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
- 掩码 Series 列表 `[mask1, mask2]`：使用掩码组合筛选

**条件元组格式说明：**
- 3 元组 `(列名, 运算符, 值)`：完整格式，如 `('age', '>', 25)`
- 2 元组 `(列名, 值)`：简写格式，默认为 `==` 比较，如 `('status', 'active')` 等价于 `('status', '==', 'active')`
- 2 元组 `(列名, null 运算符)`：空值判断，支持 `null`、`not null`、`empty`、`not empty`，如 `('email', 'null')`

## 掩码构建函数

如果需要更底层的控制，可以直接使用掩码构建函数。详见 [mask.md](./mask.md)。

## pd_count - 条件统计

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
