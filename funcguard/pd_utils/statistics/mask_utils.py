import numpy as np
import pandas as pd
from typing import List, Tuple, Optional



def _is_empty(x):
    """检查值是否为空（NaN/None、空字符串、空列表、空元组、空字典、空集合）"""
    # 处理 numpy/pandas 数组类型
    if isinstance(x, (np.ndarray, pd.Series)):
        return x.size == 0
    if pd.isna(x):
        return True
    if isinstance(x, (str, list, tuple, dict, set)):
        return len(x) == 0
    return False


def _is_not_empty(x):
    """检查值是否非空（与_is_empty相反）"""
    # 处理 numpy/pandas 数组类型
    if isinstance(x, (np.ndarray, pd.Series)):
        return x.size > 0
    if pd.isna(x):
        return False
    if isinstance(x, (str, list, tuple, dict, set)):
        return len(x) > 0
    return True


def build_single_mask(df: pd.DataFrame, condition: Tuple) -> pd.Series:
    """
    构建单个掩码，用于简单条件判断

    参数：
    - df (pd.DataFrame)：输入的DataFrame
    - condition (Tuple)：条件元组，包含(列名, 运算符, 值)
        **注意**：null, not null, empty, not empty
            # null/not null：仅判断 NaN/None
            # empty/not empty：同时覆盖 NaN/None 和空字符串 ""

    返回：
    - pd.Series：布尔掩码，True表示符合条件的行
        **注意**：此Series是通过原生pandas表达式(df[col] > value)直接返回，
        无额外内存分配和位运算，性能最优。适用于简单单一条件场景。
    """
    _NULL_OPS = {"null", "not null", "empty", "not empty"}

    if len(condition) == 2:
        column, op = condition
        if op in _NULL_OPS:
            value = None  # null / not null 不需要 value
        else:
            # 2元组且非 null 运算符，视为默认 == 比较
            # 例如 ('status', 'active') => ('status', '==', 'active')
            value = op
            op = "=="
            
    elif len(condition) == 3:
        column, op, value = condition
    else:
        raise ValueError(
            f"条件元组长度不合法: {len(condition)}，"
            "支持 2元组 (列名, 值) 或 (列名, null运算符)，3元组 (列名, 运算符, 值)"
        )

    if op == ">":
        return df[column] > value
    elif op == ">=":
        return df[column] >= value

    elif op == "<":
        return df[column] < value
    elif op == "<=":
        return df[column] <= value

    elif op == "==":
        return df[column] == value
    elif op == "!=":
        return df[column] != value

    elif op == "in":
        return df[column].isin(value)
    elif op == "not in":
        return ~df[column].isin(value)

    elif op == "null":
        return df[column].isnull()
    elif op == "not null":
        return df[column].notnull()

    elif op == "empty":
        return df[column].apply(_is_empty)
    elif op == "not empty":
        return df[column].apply(_is_not_empty)

    elif op == "contains":
        return df[column].str.contains(value, na=False)
    elif op == "not contains":
        return ~df[column].str.contains(value, na=False)

    elif op == "startswith":
        return df[column].str.startswith(value, na=False)
    elif op == "endswith":
        return df[column].str.endswith(value, na=False)
    else:
        raise ValueError(f"不支持的运算符: {op}")


def build_base_mask(
    df: pd.DataFrame,
    conditions: List[Tuple],
    logic: str = "and",
    true_mask: Optional[pd.Series] = None,
    false_mask: Optional[pd.Series] = None,
) -> pd.Series:
    """
    构建基础查询条件掩码

    参数：
    - df (pd.DataFrame)：输入的DataFrame
    - conditions (List[Tuple])：条件列表，每个元组包含(列名, 运算符, 值)
    - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"
    - true_mask (pd.Series)：初始True掩码，默认为None
    - false_mask (pd.Series)：初始False掩码，默认为None

    返回：
    - pd.Series：布尔掩码，True表示符合条件的行
        **注意**：此Series是通过pd.Series([True/False] * len(df))创建的新对象，
        并经过多个条件组合的位运算(&/|)生成，适用于复杂多条件场景，
        存在内存分配，会占用一定内存，相比原生pandas表达式有一定性能开销。

    说明：
    - 如需复杂的嵌套逻辑组合，请使用 combine_masks 方法。
    """
    if logic == "and":
        mask = (
            true_mask
            if true_mask is not None
            else pd.Series([True] * len(df), index=df.index)
        )
        operator_func = lambda m, c: m & c
    elif logic == "or":
        mask = (
            false_mask
            if false_mask is not None
            else pd.Series([False] * len(df), index=df.index)
        )
        operator_func = lambda m, c: m | c
    else:
        raise ValueError(f"不支持的逻辑操作类型: {logic}，支持 'and' 或 'or'")

    for condition in conditions:
        condition_mask = build_single_mask(df, condition)
        mask = operator_func(mask, condition_mask)

    return mask


def combine_masks(masks: List[pd.Series], logic: str = "and") -> pd.Series:
    """
    合并多个布尔掩码，支持复杂的嵌套逻辑组合

    参数：
    - masks (List[pd.Series])：布尔掩码列表
    - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"

    返回：
    - pd.Series：合并后的布尔掩码
        **注意**：此Series是通过pd.Series([True/False] * len(masks[0]))创建的新对象，
        并经过多个掩码的位运算组合生成，适用于超复杂嵌套逻辑场景。

    示例：
    # 复杂逻辑组合：(age > 18 AND score >= 60) OR (status == "special")
        mask1 = build_base_mask(df, [("age", ">", 18), ("score", ">=", 60)])
        mask2 = build_base_mask(df, [("status", "==", "special")])
        combined_mask = combine_masks([mask1, mask2], logic="or")
    """
    if not masks:
        raise ValueError("掩码列表不能为空")

    if logic == "and":
        result_mask = pd.Series([True] * len(masks[0]), index=masks[0].index)
        for mask in masks:
            result_mask &= mask
    elif logic == "or":
        result_mask = pd.Series([False] * len(masks[0]), index=masks[0].index)
        for mask in masks:
            result_mask |= mask
    else:
        raise ValueError(f"不支持的逻辑操作类型: {logic}，支持 'and' 或 'or'")

    return result_mask
