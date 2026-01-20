import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_timedelta64_dtype
from typing import Union, List, Any, Dict


def fill_null(
    df: pd.DataFrame, columns: Union[List[str], Dict[str, Any]], fill_value: Any
) -> pd.DataFrame:
    """
    替换DataFrame中指定列的空值为指定值。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (List[str] or Dict[str, Any])：
        要替换空值的列名列表或字典， 键为列名，值为要填充的值。
    - fill_value (Any, optional)：要填充的值。

    返回：
    - pd.DataFrame：替换空值后的DataFrame。
    """
    if isinstance(columns, list):
        for column in columns:
            df[column] = df[column].fillna(fill_value)
    elif isinstance(columns, dict):
        for column, value in columns.items():
            df[column] = df[column].fillna(value)
    return df


def round_columns(
    df: pd.DataFrame, columns: List[str], digits: int = 0
) -> pd.DataFrame:
    """
    对DataFrame中指定列进行四舍五入操作。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (List[str])：要进行四舍五入的列名列表。
    - digits (int, optional)：保留的小数位数，默认为0。

    返回：
    - pd.DataFrame：四舍五入后的DataFrame。
    """
    for column in columns:
        if column in df.columns:
            df[column] = df[column].round(digits)
    return df


def fill_nat(
    df: pd.DataFrame, columns: Union[List[str], str]
) -> pd.DataFrame:
    """将指定列的 NaT（Datetime/Timedelta）替换为空字符串"""

    if isinstance(columns, str):
        columns = [columns]

    for column in columns:
        if column not in df.columns:
            continue
        column_dtype = df[column].dtype
        if is_datetime64_any_dtype(column_dtype) or is_timedelta64_dtype(
            column_dtype
        ):
            column_as_object = df[column].astype(object)
            df[column] = column_as_object.fillna("")
    return df