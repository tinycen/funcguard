import json
from typing import Any


def json_loads(value: Any, empty_to_dict: bool = True) -> Any:
    """
    将JSON字符串解析为Python对象。

    参数：
    - value: 要解析的值
    - empty_to_dict: 是否将空字符串转换为{}，默认为 True

    返回：
    - 解析后的Python对象，或原始值（如果解析失败）
    """
    # 如果不是字符串，直接返回原值
    if not isinstance(value, str):
        return value

    # 处理空字符串
    if not value.strip():
        return {} if empty_to_dict else value

    # 尝试解析JSON字符串
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        # 解析失败，返回原值
        raise ValueError(f"JSON解析错误：{value}")