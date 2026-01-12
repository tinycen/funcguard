import pandas as pd
from decimal import Decimal

# 启用未来行为：禁止静默降级
pd.set_option("future.no_silent_downcasting", True)

from typing import Union, List, Dict, Any
from pandas import Int64Dtype, Float64Dtype, StringDtype, BooleanDtype  # pyright: ignore

# 数据类型映射常量
TYPE_MAPPING = {
    'int': Int64Dtype(),
    'float': Float64Dtype(), 
    'str': StringDtype(),
    'bool': BooleanDtype(),
    'datetime': 'datetime64[ns]'  # datetime使用字符串形式
}


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


# 对指定列进行四舍五入
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


# 转换指定列的数据类型
def convert_columns_type(
    df: pd.DataFrame, columns: Dict[str, str]
) -> pd.DataFrame:
    """
    转换DataFrame中指定列的数据类型。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (Dict[str, str])：
        要转换类型的字典，键为列名，值为目标数据类型。
        支持的数据类型：'int', 'float', 'str', 'bool', 'datetime'。

    返回：
    - pd.DataFrame：列类型转换后的DataFrame。
    """
    for column, target_type in columns.items():
        if column in df.columns and target_type in TYPE_MAPPING:
            try:
                if target_type == 'datetime':
                    df[column] = pd.to_datetime(df[column], errors='coerce')
                else:
                    df[column] = df[column].astype(TYPE_MAPPING[target_type])  # pyright: ignore[reportArgumentType]
            except (ValueError, TypeError):
                # 如果转换失败，保持原类型
                pass
    return df
