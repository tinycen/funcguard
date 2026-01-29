import pandas as pd
from typing import List, Tuple, Union, Optional
from .mask_utils import build_single_mask, build_base_mask


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
