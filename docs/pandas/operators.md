# 支持的运算符

本文档描述的条件运算符适用于以下函数/方法：

| 函数/方法 | 说明 |
|-----------|------|
| `pd_filter` | 数据过滤 |
| `pd_count` | 条件计数 |
| `pd_value_counts` | 不同值计数统计 |
| `pd_group_agg` | 分组聚合统计 |
| `DataFrameStatistics.build_single_mask` | 单条件掩码构建 |
| `DataFrameStatistics.build_base_mask` | 多条件掩码构建 |

支持的运算符列表如下：

| 类型 | 操作符 | 说明 | 示例 |
|------|--------|------|------|
| 比较运算 | `>`, `>=`, `<`, `<=`, `==`, `!=` | 数值/字符串比较 | `('age', '>', 25)` |
| 集合运算 | `in`, `not in` | 在/不在集合中 | `('status', 'in', ['A', 'B'])` |
| 空值判断 | `null`, `not null` | 为空（仅判断 NaN/None） | `('email', 'null')` |
| 空字符串判断 | `empty`, `not empty` | 为空（同时覆盖 NaN/None 和空字符串 ""） | `('phone', 'not empty')` |
| 字符串匹配 | `startswith`, `endswith` | 以指定字符串开头/结尾 | `('code', 'startswith', 'A')` |
| 字符串匹配 | `contains`, `not contains` | 包含/不包含字符串 | `('name', 'contains', '张')` |
