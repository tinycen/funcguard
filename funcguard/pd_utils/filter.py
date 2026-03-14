import pandas as pd
from typing import Union, List, Tuple

from .statistics.mask_utils import build_single_mask, build_base_mask, combine_masks


def pd_filter(
    df: pd.DataFrame,
    conditions: Union[Tuple, List[Tuple], List[pd.Series]],
    logic: str = "and"
) -> pd.DataFrame:
    """
    根据条件筛选DataFrame数据

    智能识别条件类型，自动选择合适的掩码构建方式：
    - 单个条件元组：使用 build_single_mask（性能最优）
    - 条件元组列表：使用 build_base_mask
    - 掩码Series列表：使用 combine_masks

    参数：
    - df (pd.DataFrame)：输入的DataFrame
    - conditions：筛选条件，支持三种格式：
        1. 单个条件元组：(列名, 运算符, 值)
           例如：('age', '>', 25)
           对于 null/not null 运算符：(列名, 运算符)
           例如：('email', 'null')

        2. 条件元组列表：[(列名, 运算符, 值), ...]
           例如：[('age', '>', 25), ('salary', '>', 5000)]

        3. 掩码Series列表：[pd.Series, pd.Series, ...]
           例如：[mask1, mask2]

    - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"
        仅对条件元组列表和掩码Series列表有效

    返回：
    - pd.DataFrame：筛选后的DataFrame

    支持的运算符：
    - 比较运算：>, >=, <, <=, ==, !=
    - 集合运算：in, not in
    - 空值判断：null, not null
    - 字符串匹配：contains, not contains, startswith, endswith

    示例：
    # 单个条件筛选
    filtered_df = pd_filter(df, ('age', '>', 25))

    # 多个条件 AND 筛选
    filtered_df = pd_filter(df, [
        ('age', '>', 25),
        ('salary', '>', 5000)
    ], logic='and')

    # 多个条件 OR 筛选
    filtered_df = pd_filter(df, [
        ('dept', '==', 'IT'),
        ('dept', '==', 'HR')
    ], logic='or')

    # 空值判断
    filtered_df = pd_filter(df, ('email', 'null'))
    filtered_df = pd_filter(df, ('phone', 'not null'))

    # 字符串匹配
    filtered_df = pd_filter(df, ('name', 'contains', '张'))

    # 组合多个掩码
    mask1 = pd_filter(df, [('age', '>', 25), ('salary', '>', 5000)])
    mask2 = pd_filter(df, ('dept', '==', 'IT'))
    filtered_df = pd_filter(df, [mask1, mask2], logic='or')
    """
    if df.empty:
        return df.copy()

    # 情况1：单个条件元组
    if isinstance(conditions, tuple):
        mask = build_single_mask(df, conditions)
        return df[mask].copy()

    # 情况2：空列表
    if not conditions:
        return df.copy()

    # 判断列表中的元素类型
    first_item = conditions[0]

    # 情况3：掩码Series列表
    if isinstance(first_item, pd.Series):
        mask = combine_masks(conditions, logic=logic)  # type: ignore[arg-type]
        return df[mask].copy()

    # 情况4：条件元组列表
    if isinstance(first_item, tuple):
        mask = build_base_mask(df, conditions, logic=logic)  # type: ignore[arg-type]
        return df[mask].copy()

    raise ValueError(
        f"不支持的条件类型: {type(first_item)}。"
        "请使用 Tuple（单个条件）、List[Tuple]（多个条件）或 List[pd.Series]（掩码列表）"
    )
