import pandas as pd
from pandas.api.types import is_datetime64_any_dtype, is_timedelta64_dtype
from typing import Any
from .convert_utils import convert_numeric_series


def fill_na(
    df: pd.DataFrame,
    columns: list[str] | dict[str, Any],
    fill_value: Any = "",
    decimal_places: int | None = None,
    copy: bool = False,
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
    - copy (bool, optional)：是否在副本上操作而非修改原 DataFrame，默认 False。

    返回：
    - pd.DataFrame：替换空值后的DataFrame。

    注意：当 copy=False 时，本函数直接修改传入的 DataFrame。
    如需保留原数据，请设置 copy=True 或在调用前使用 df.copy()。
    """
    if copy:
        df = df.copy()
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
