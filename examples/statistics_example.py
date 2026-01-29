# DataFrame统计分析模块使用示例

from funcguard.pd_utils.df_statistics import DataFrameStatistics, create_statistics
import pandas as pd

# 创建示例数据
df = pd.DataFrame({
    'age': [25, 30, 35, 40, 45, 50, 55, 60],
    'salary': [5000, 6000, 7000, 8000, 9000, 10000, 11000, 12000],
    'score': [80, 85, 90, 75, 88, 92, 78, 85],
    'status': ['active', 'inactive', 'active', 'active', 'inactive', 'active', 'active', 'inactive']
})

# 方法1：使用统计类（推荐用于多次统计）
print("=== 方法1：使用DataFrameStatistics类 ===")
stats = create_statistics(df)

# 多次统计操作，复用基础Series对象
count1 = stats.count([('age', '>', 30), ('salary', '>=', 7000)])
count2 = stats.count([('status', '==', 'active')])
count3 = stats.count([('score', '>=', 80)])

print(f"年龄>30且薪资>=7000的人数: {count1}")
print(f"状态为active的人数: {count2}")
print(f"分数>=80的人数: {count3}")

# 方法2：批量统计（更高效的多次统计）
print("\n=== 方法2：批量统计 ===")
condition_groups = [
    {'conditions': [('age', '>', 35), ('salary', '>=', 8000)]},
    {'conditions': [('status', '==', 'active'), ('score', '>=', 85)]},
    {'conditions': [('salary', '>=', 9000)]}
]

results = stats.batch_count(condition_groups)
print("批量统计结果:", results)

# 方法3：兼容原函数接口（单次统计）
print("\n=== 方法3：兼容原函数接口 ===")
from funcguard.pd_utils.df_statistics import count

single_count = count(df, [('age', '>', 40)])
print(f"年龄>40的人数: {single_count}")

# 查看DataFrame信息
print("\n=== DataFrame信息 ===")
info = stats.get_dataframe_info()
print(f"数据形状: {info['shape']}")
print(f"内存使用: {info['memory_usage']} bytes")