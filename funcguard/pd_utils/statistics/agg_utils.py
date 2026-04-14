
"""
聚合(aggregation)操作工具模块。

提供DataFrame分组聚合统计功能，支持按指定列分组后对另一列进行
sum、mean、max、min、count、median、std、var等聚合计算。
"""

import pandas as pd
from typing import Any, Dict, Optional, Union, List, Tuple
from .mask_utils import build_single_mask, build_base_mask


def group_agg(
    df: pd.DataFrame,
    group_col: str,
    agg_col: str,
    agg_func: str = "sum",
    sort: Optional[str] = None,
    conditions: Optional[Union[Tuple, List[Tuple]]] = None,
    logic: str = "and",
    true_mask: Optional[pd.Series] = None,
    false_mask: Optional[pd.Series] = None,
    to_dict: bool = True
) -> Dict[Any, Union[int, float]]:
    """
    按指定列分组，对另一列进行聚合统计。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - group_col (str)：分组列名（如A列）。
    - agg_col (str)：聚合列名（如B列）。
    - agg_func (str)：聚合函数，支持 "sum"、"mean"、"max"、"min"、"count"、"median"、"std"、"var"，
        默认为 "sum"。
    - sort (Optional[str])：排序方式，"asc" 表示升序，"desc" 表示降序，
        默认为None表示按分组列的原始顺序。
    - conditions (Optional[Union[Tuple, List[Tuple]]])：可选的过滤条件，
        格式与count函数相同。如果提供，则只统计符合条件的行。
    - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"。
    - true_mask (pd.Series)：初始True掩码，默认为None。
    - false_mask (pd.Series)：初始False掩码，默认为None。
    - to_dict (bool)：是否将结果转换为字典，默认为True。

    返回：
    - Dict[Any, Union[int, float]]：以分组值为键，聚合结果为值的字典。

    示例：
        >>> group_agg(df, "category", "amount", "sum")
        {'A': 1000, 'B': 2000, 'C': 1500}
        >>> group_agg(df, "category", "amount", "mean")
        {'A': 100.0, 'B': 200.0, 'C': 150.0}
        >>> group_agg(df, "category", "amount", "sum", sort="desc")
        {'B': 2000, 'C': 1500, 'A': 1000}
        >>> group_agg(df, "category", "amount", "sum", conditions=[("status", "==", "active")])
        {'A': 800, 'B': 1500}
    """
    # 参数校验
    valid_agg_funcs = ("sum", "mean", "max", "min", "count", "median", "std", "var")
    if agg_func not in valid_agg_funcs:
        raise ValueError(f"agg_func 参数必须是 {valid_agg_funcs} 之一，当前值: {agg_func}")
    if sort is not None and sort not in ("asc", "desc"):
        raise ValueError(f"sort 参数必须是 'asc'、'desc' 或 None，当前值: {sort}")

    # 如果有过滤条件，先应用条件筛选
    if conditions is not None:
        if isinstance(conditions, tuple):
            mask = build_single_mask(df, conditions)
        else:
            mask = build_base_mask(df, conditions, logic, true_mask, false_mask)
        filtered_df = df[mask]
    else:
        filtered_df = df

    # 使用pandas的groupby进行聚合
    grouped = filtered_df.groupby(group_col)[agg_col]
    result_series = grouped.agg(agg_func)

    # 排序处理
    if sort == "asc":
        result_series = result_series.sort_values(ascending=True)
    elif sort == "desc":
        result_series = result_series.sort_values(ascending=False)
    
    # 转换为字典返回
    if to_dict:
        return result_series.to_dict()
    else:
        return result_series
