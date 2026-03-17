import pandas as pd
from datetime import datetime
from pandas.api.types import is_datetime64_any_dtype, is_timedelta64_dtype, is_numeric_dtype
from typing import Union, List, Any, Dict, Optional
from .convert_utils import convert_numeric_series


def fill_na(
    df: pd.DataFrame,
    columns: Union[List[str], Dict[str, Any]],
    fill_value: Any = "",
    decimal_places: Optional[int] = None,
) -> pd.DataFrame:
    """
    替换DataFrame中指定列的空值为指定值。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (List[str] or Dict[str, Any])：
        * 如果为List[str]，则使用fill_value填充指定列的空值
        * 如果为Dict[str, Any]，则使用字典中对应列的value填充空值（键为列名，值为填充值）
        * 如果为List[str]且为空列表，则对所有列应用fill_value填充
    - fill_value (Any, optional)：当columns为列表时的默认填充值，默认为空字符串。
    - decimal_places (int, optional)：当进行数值转换时保留的小数位数，默认为None表示不限制

    返回：
    - pd.DataFrame：替换空值后的DataFrame。
    """
    _is_numeric_fill = isinstance(fill_value, (int, float))

    if isinstance(columns, list):
        if len(columns) == 0:
            if _is_numeric_fill:
                df = df.fillna(fill_value)
                for col in df.columns:
                    df[col] = convert_numeric_series(df[col], decimal_places)
            else:
                df = df.fillna(fill_value)
        else:
            for column in columns:
                if _is_numeric_fill:
                    df[column] = df[column].astype(float).fillna(fill_value)
                    df[column] = convert_numeric_series(df[column], decimal_places)
                else:
                    df[column] = df[column].fillna(fill_value)
    elif isinstance(columns, dict):
        for column, value in columns.items():
            if column not in df.columns:
                continue
            try:
                if isinstance(value, (int, float)):
                    # 检查列是否为日期时间类型，避免直接转float报错
                    if is_datetime64_any_dtype(df[column].dtype) or is_timedelta64_dtype(df[column].dtype):
                        # 日期类型不能直接填充数值，直接使用 fillna() 填充而不转换为 float
                        df[column] = df[column].fillna(value)
                    else:
                        df[column] = df[column].astype(float).fillna(value)
                        df[column] = convert_numeric_series(df[column], decimal_places)
                else:
                    df[column] = df[column].fillna(value)
            except Exception as e:
                column_dtype = df[column].dtype
                raise TypeError(f"处理列 '{column}' (类型: {column_dtype}) 时出错: {e}") from e
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
    new_date: Union[str, datetime],
    unit: str = "h",
    decimal_places: int = 1,
    nat: Optional[int] = None
) -> pd.DataFrame:
    """
    计算DataFrame中两列日期的时间差，并将结果填充到指定列。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - target_column (str)：要填充计算结果的列名。
    - old_date_column (str)：原始日期列名。
    - new_date (str | datetime)：新日期，可以是列名字符串或datetime对象。
    - unit (str, optional)：返回单位，"h" 返回小时数，"d" 返回天数，默认为"h"。
    - decimal_places (int, optional)：保留的小数位数，默认为1。
    - nat (int, optional)：当日期为NaT时的填充值，默认为None表示不特殊处理。

    返回：
    - pd.DataFrame：填充计算结果后的DataFrame。
    """
    if old_date_column not in df.columns:
        raise ValueError(f"列 '{old_date_column}' 不存在于DataFrame中")

    old_date = df[old_date_column]

    # 如果日期列为字符串类型（object 或 string），则转换为 datetime 类型
    # errors="coerce" 表示将无法解析的日期字符串转换为 NaT（Not a Time），而不是抛出错误
    if old_date.dtype == object or str(old_date.dtype) == "string":
        old_date = pd.to_datetime(old_date, errors="coerce")

    # 判断 new_date 是列名字符串还是 datetime 对象
    if isinstance(new_date, str):
        if new_date not in df.columns:
            raise ValueError(f"列 '{new_date}' 不存在于DataFrame中")
        new_date_values = df[new_date]
        # 如果日期列为字符串类型，则转换为 datetime 类型
        if new_date_values.dtype == object or str(new_date_values.dtype) == "string":
            new_date_values = pd.to_datetime(new_date_values, errors="coerce")
    elif isinstance(new_date, datetime):
        new_date_values = new_date
    else:
        raise TypeError("new_date 必须是字符串（列名）或 datetime 对象")

    diff_seconds = (new_date_values - old_date).dt.total_seconds()  # pyright: ignore[reportAttributeAccessIssue]

    if unit == "h":
        result = round(diff_seconds / 3600, decimal_places)
    elif unit == "d":
        result = round(diff_seconds / 86400, decimal_places)
    else:
        raise ValueError("unit must be 'h' or 'd'")
    
    # 确保结果是数值类型，而不是 Timedelta 类型
    if decimal_places > 0:
        result = result.astype(float)
    else:
        result = result.astype(int)

    # 如果指定了 nat，将 NaT 对应的结果替换为 nat
    if nat is not None:
        # 检测 old_date 或 new_date_values 中的 NaT
        if isinstance(new_date_values, pd.Series):
            nat_mask = old_date.isna() | new_date_values.isna()
        else:
            nat_mask = old_date.isna()
        result = result.where(~nat_mask, nat)

    df[target_column] = result

    return df