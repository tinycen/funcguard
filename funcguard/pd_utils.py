import pandas as pd
from decimal import Decimal

# 启用未来行为：禁止静默降级
pd.set_option("future.no_silent_downcasting", True)

from typing import Union, List, Dict, Any


# 替换指定列的空值为指定值
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
