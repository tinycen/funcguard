# 掩码构建

FuncGuard 提供灵活的掩码构建函数，用于构建布尔掩码进行数据筛选。这些函数返回布尔掩码而不是筛选后的 DataFrame。

掩码构建函数支持从 `funcguard` 直接导入使用。

## pd_build_mask - 单个条件掩码

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

# 空值判断（仅判断 NaN/None）
mask = pd_build_mask(df, ('email', 'null'))
mask = pd_build_mask(df, ('phone', 'not null'))

# 空值/空容器判断（覆盖 NaN/None、空字符串、空列表、空元组、空字典、空集合）
mask = pd_build_mask(df, ('tags', 'empty'))      # 筛选空列表/空元组等
mask = pd_build_mask(df, ('segments', 'not empty'))  # 筛选非空值

# 字符串匹配
mask = pd_build_mask(df, ('name', 'contains', '张'))
mask = pd_build_mask(df, ('email', 'startswith', 'admin'))
mask = pd_build_mask(df, ('file', 'endswith', '.pdf'))

# 应用掩码筛选数据
filtered_df = df[mask]
```

## pd_build_masks - 多个条件掩码

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

## pd_combine_masks - 掩码组合

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

# 组合掩码（OR 逻辑）
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

## 支持的运算符

掩码构建支持 [operators.md](./operators.md) 中列出的所有运算符。
