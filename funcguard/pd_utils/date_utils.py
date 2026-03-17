import pandas as pd
from datetime import datetime
from pandas.api.types import is_datetime64_any_dtype, is_timedelta64_dtype
from typing import Union, List, Any, Optional


# 单位 -> 对应秒数
_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400}


def _resolve_date(df: pd.DataFrame, date: Union[str, datetime]) -> pd.Series:
    """将列名或 datetime 统一转换为 pd.Series"""
    if isinstance(date, datetime):
        return pd.Series([date] * len(df), index=df.index)
    if date not in df.columns:
        raise ValueError(f"列 '{date}' 不存在于DataFrame中")
    s = df[date]
    if s.dtype == object or str(s.dtype) == "string":
        s = pd.to_datetime(s, errors="coerce")
    return s


def fill_nat(
    df: pd.DataFrame, columns: Union[List[str], str], fill_value: Any = ""
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
    old_date: Union[str, datetime],
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
    - old_date (str | datetime)：原始日期，可以是列名字符串或datetime对象。
    - new_date (str | datetime)：新日期，可以是列名字符串或datetime对象。
    - unit (str, optional)：返回单位，"h" 返回小时数，"d" 返回天数，"m" 返回分钟数，"s" 返回秒数，默认为"h"。
    - decimal_places (int, optional)：保留的小数位数，默认为1。
    - nat (int, optional)：当日期为NaT时的填充值，默认为None表示不特殊处理。

    返回：
    - pd.DataFrame：填充计算结果后的DataFrame。
    """
    if unit not in _UNIT_SECONDS:
        raise ValueError(f"unit 须为 {set(_UNIT_SECONDS)} 之一")

    old_vals = _resolve_date(df, old_date)
    new_vals = _resolve_date(df, new_date)

    nat_mask = old_vals.isna() | new_vals.isna()
    if nat_mask.any() and nat is None:
        raise ValueError(
            f"'{old_date}' 或 '{new_date}' 中存在 NaT，请设置 nat 参数指定填充值"
        )

    result = (new_vals - old_vals).dt.total_seconds()  # pyright: ignore[reportAttributeAccessIssue]
    result = result / _UNIT_SECONDS[unit]
    result = result.round(decimal_places)

    if nat is not None:
        result = result.where(~nat_mask, nat)

    df[target_column] = result.astype(float if decimal_places > 0 else int)
    return df