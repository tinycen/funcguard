import pandas as pd
from typing import List, Tuple, Union, Optional, Dict, Any, Mapping
from .mask_utils import build_single_mask, build_base_mask


def value_counts(
    df: pd.DataFrame,
    column: str,
    mode: str = "count",
    sort: Optional[str] = None,
    dropna: bool = True,
    conditions: Optional[Union[Tuple, List[Tuple]]] = None,
    logic: str = "and",
    true_mask: Optional[pd.Series] = None,
    false_mask: Optional[pd.Series] = None
) -> Mapping[Any, Union[int, float]]:
    """
    统计DataFrame指定列中不同值的计数数据。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - column (str)：要统计的列名。
    - mode (str)：统计模式，"count" 表示计数，"percent" 表示百分比，默认为 "count"。
    - sort (Optional[str])：排序方式，"asc" 表示升序，"desc" 表示降序，
        默认为None表示不排序。
    - dropna (bool)：是否排除空值，默认为True。
    - conditions (Optional[Union[Tuple, List[Tuple]]])：可选的过滤条件，
        格式与count函数相同。如果提供，则只统计符合条件的行。
    - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"。
    - true_mask (pd.Series)：初始True掩码，默认为None。
    - false_mask (pd.Series)：初始False掩码，默认为None。

    返回：
    - Mapping[Any, Union[int, float]]：以值为键，计数/百分比为值的字典。

    示例：
        >>> value_counts(df, "status")
        {'active': 150, 'inactive': 50, 'pending': 20}
        >>> value_counts(df, "status", mode="percent")
        {'active': 0.6818, 'inactive': 0.2273, 'pending': 0.0909}
        >>> value_counts(df, "status", sort="desc")
        {'active': 150, 'inactive': 50, 'pending': 20}
        >>> value_counts(df, "status", sort="asc")
        {'pending': 20, 'inactive': 50, 'active': 150}
        >>> value_counts(df, "status", conditions=[("age", ">", 18)])
        {'active': 120, 'inactive': 30}
    """
    # 参数校验
    if mode not in ("count", "percent"):
        raise ValueError(f"mode 参数必须是 'count' 或 'percent'，当前值: {mode}")
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

    # 转换参数
    normalize = mode == "percent"
    do_sort = sort is not None
    ascending = sort == "asc" if do_sort else False

    # 使用pandas的value_counts方法统计
    result_series = filtered_df[column].value_counts(
        normalize=normalize,
        sort=do_sort,
        ascending=ascending,
        dropna=dropna
    )

    # 转换为字典返回
    return result_series.to_dict()


def count(
    df: pd.DataFrame,
    conditions: Union[Tuple, List[Tuple]],
    logic: str = "and",
    true_mask: Optional[pd.Series] = None,
    false_mask: Optional[pd.Series] = None
) -> int:
    """
    使用int sum 方法，统计DataFrame中符合条件的非空值数量。
    - 该方法将DataFrame中符合条件的行转换为布尔值（True/False），
    - 然后使用sum方法计算True的数量。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - conditions (Union[Tuple, List[Tuple]])：符合条件的表达式。
        每个元组包含三部分：列名、运算符（例如 ">"、"<"、"=="、"!=" ）和值。 示例：
        示例1：元组 ("column", ">", 0)
        示例2：列表 [("column", ">", 0), ("column2", "==", "value")]。

    - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"
    - true_mask (pd.Series)：初始True掩码，默认为None
    - false_mask (pd.Series)：初始False掩码，默认为None

    返回：
    - int：符合条件的数量。
    """
    # 单一条件
    if isinstance(conditions, tuple):
        mask = build_single_mask(df, conditions)
        return int(mask.sum())

    # 使用独立的函数构建查询条件掩码
    mask = build_base_mask(df, conditions, logic, true_mask, false_mask)

    # 使用sum方法计算True的数量（True被视为1，False被视为0）
    return int(mask.sum())
