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

## 性能优化

DataFrameStatistics 类通过以下方式优化性能：
1. **缓存基础掩码**：避免重复创建 pd.Series([True] * len(df))
2. **复用 DataFrame 索引**：减少内存分配
3. **批量统计功能**：减少函数调用开销
4. **原生 pandas 表达式**：简单条件直接使用原生表达式，无额外内存分配
