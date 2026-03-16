import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_timedelta64_dtype, is_numeric_dtype
from typing import Union, List, Any, Dict


def fill_na(
    df: pd.DataFrame,
    columns: Union[List[str], Dict[str, Any]],
    fill_value: Any = ""
) -> pd.DataFrame:
    """
    替换DataFrame中指定列的空值为指定值。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (List[str] or Dict[str, Any])：
        要替换空值的列名列表或字典， 键为列名，值为要填充的值。
    - fill_value (Any, optional)：要填充的值，默认为空字符串。

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
    df: pd.DataFrame, columns: List[str], decimal_places: int = 0
) -> pd.DataFrame:
    """
    对DataFrame中指定列进行四舍五入操作。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (List[str])：要进行四舍五入的列名列表。
    - decimal_places (int, optional)：保留的小数位数，默认为0。

    返回：
    - pd.DataFrame：四舍五入后的DataFrame。
    """
    for column in columns:
        if column in df.columns:
            if not is_numeric_dtype(df[column]):
                raise TypeError(f"列 '{column}' 不是数值类型，无法执行四舍五入操作")
            df[column] = df[column].round(decimal_places)
    return df


def fill_nat(
    df: pd.DataFrame, columns: Union[List[str], str],fill_value: Any = ""
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
            df[column] = column_as_object.fillna(fill_value)
        else:
            df[column] = df[column].replace({pd.NaT: fill_value, "NaT": fill_value})
    return df


def cal_date_diff(
    df: pd.DataFrame,
    target_column: str,
    old_date_column: str,
    new_date_column: str,
    unit: str = "h",
    decimal_places: int = 1
) -> pd.DataFrame:
    """
    计算DataFrame中两列日期的时间差，并将结果填充到指定列。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - target_column (str)：要填充计算结果的列名。
    - old_date_column (str)：原始日期列名。
    - new_date_column (str)：新日期列名。
    - unit (str, optional)：返回单位，"h" 返回小时数，"day" 返回天数，默认为"h"。
    - decimal_places (int, optional)：保留的小数位数，默认为1。

    返回：
    - pd.DataFrame：填充计算结果后的DataFrame。
    """
    if old_date_column not in df.columns:
        raise ValueError(f"列 '{old_date_column}' 不存在于DataFrame中")
    if new_date_column not in df.columns:
        raise ValueError(f"列 '{new_date_column}' 不存在于DataFrame中")

    old_date = df[old_date_column]
    new_date = df[new_date_column]

    # 如果日期列为字符串类型（object 或 string），则转换为 datetime 类型
    # errors="coerce" 表示将无法解析的日期字符串转换为 NaT（Not a Time），而不是抛出错误
    if old_date.dtype == object or str(old_date.dtype) == "string":
        old_date = pd.to_datetime(old_date, errors="coerce")
    if new_date.dtype == object or str(new_date.dtype) == "string":
        new_date = pd.to_datetime(new_date, errors="coerce")

    diff_seconds = (new_date - old_date).dt.total_seconds()  # pyright: ignore[reportAttributeAccessIssue]

    if unit == "h":
        df[target_column] = round(diff_seconds / 3600, decimal_places)
    elif unit == "day":
        df[target_column] = round(diff_seconds / 86400, decimal_places)
    else:
        raise ValueError("unit must be 'h' or 'day'")

    return df