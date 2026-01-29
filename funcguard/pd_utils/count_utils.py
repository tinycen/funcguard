import pandas as pd
from typing import Union, List, Any, Dict, Tuple

def build_base_mask(df: pd.DataFrame, conditions: List[Tuple], logic: str = "and") -> pd.Series:
    """
    构建基础查询条件掩码
    
    参数：
    - df (pd.DataFrame)：输入的DataFrame
    - conditions (List[Tuple])：条件列表，每个元组包含(列名, 运算符, 值)
    - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"
    
    返回：
    - pd.Series：布尔掩码，True表示符合条件的行
    
    说明：
    这是基础的条件构建函数，用于创建单个逻辑组的条件掩码。
    如需复杂的嵌套逻辑组合，请使用 combine_masks 方法。
    """
    if logic == "and":
        mask = pd.Series([True] * len(df), index=df.index)
        operator_func = lambda m, c: m & c
    elif logic == "or":
        mask = pd.Series([False] * len(df), index=df.index)
        operator_func = lambda m, c: m | c
    else:
        raise ValueError(f"不支持的逻辑操作类型: {logic}，支持 'and' 或 'or'")
    
    for column, op, value in conditions:
        if op == ">":
            condition_mask = df[column] > value
        elif op == ">=":
            condition_mask = df[column] >= value
        elif op == "<":
            condition_mask = df[column] < value
        elif op == "<=":
            condition_mask = df[column] <= value
        elif op == "==":
            condition_mask = df[column] == value
        elif op == "!=":
            condition_mask = df[column] != value
        else:
            raise ValueError(f"不支持的运算符: {op}")
        
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
    
    示例：
    # 复杂逻辑组合：(age > 18 AND score >= 60) OR (status == "special")
    mask1 = build_base_mask(df, [("age", ">", 18), ("score", ">=", 60)], logic="and")
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

def count(df: pd.DataFrame, conditions: Union[Tuple, List[Tuple]]) -> int:
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

    返回：
    - int：符合条件的数量。
    """
    # 确保conditions是列表格式
    if isinstance(conditions, tuple):
        conditions = [conditions]
    
    # 使用独立的函数构建查询条件掩码
    mask = build_base_mask(df, conditions)
    
    # 使用sum方法计算True的数量（True被视为1，False被视为0）
    return int(mask.sum())

