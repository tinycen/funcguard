import pandas as pd
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
