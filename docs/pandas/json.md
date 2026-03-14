# JSON 处理

FuncGuard 提供 JSON 字符串解析功能，用于处理 DataFrame 中的 JSON 数据。

## load_json - JSON 字符串解析

对 DataFrame 中指定的列执行 json.loads 操作，将 JSON 字符串转换为 Python 对象。

```python
from funcguard.pd_utils import load_json

# 解析 JSON 字符串列
df = load_json(df, ['config', 'metadata'])

# 空字符串转换为字典
df = load_json(df, ['config'], empty_to_dict=True)
```
