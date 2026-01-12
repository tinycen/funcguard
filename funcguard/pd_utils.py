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

def detect_and_convert_decimal(
    df: pd.DataFrame, 
    columns: Union[List[str], Dict[str, str], None] = None,
    default_type: str = 'int'
) -> pd.DataFrame:
    """
    检测DataFrame中是否包含Decimal类型的字段，如果包含则转换为指定的数据类型。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (List[str], Dict[str, str], or None)：
        * 如果为None，则检测所有列
        * 如果为List[str]，则检测指定列，发现Decimal时转换为default_type指定的类型
        * 如果为Dict[str, str]，则键为列名，值为当发现Decimal时要转换的目标类型（支持'int'或'float'）
    - default_type (str, optional)：当columns为列表时的默认转换类型，默认为'int'。
                                支持'int'或'float'。

    返回：
    - pd.DataFrame：转换后的DataFrame。
    """
    if columns is None:
        # 检测所有列
        target_columns = df.columns.tolist()
        column_types = {col: default_type for col in target_columns}
    elif isinstance(columns, list):
        # 检测指定列，使用默认类型
        target_columns = columns
        column_types = {col: default_type for col in target_columns}
    elif isinstance(columns, dict):
        # 使用字典指定的类型
        target_columns = list(columns.keys())
        column_types = columns
    
    # 验证default_type和字典中的类型是否有效
    valid_types = {'int', 'float'}
    for col, target_type in column_types.items():
        if target_type not in valid_types:
            raise ValueError(f"无效的类型指定：{target_type}。支持的类型为：{valid_types}")
    
    for column in target_columns:
        # 检查列是否存在且为object类型 (只有object类型列才可能包含Decimal)
        if column not in df.columns or df[column].dtype != object:
            continue
        # 检查列中的第一个非空值是否是Decimal类型
        first_non_null = df[column].first_valid_index()
        if first_non_null is None:
            continue
        if isinstance(df.at[first_non_null, column], Decimal):  # pyright: ignore[reportArgumentType]
            # 根据指定的类型进行转换
            target_type = column_types[column]
            if target_type == 'int':
                df[column] = df[column].astype(int)
            elif target_type == 'float':
                df[column] = df[column].astype(float)

    return df
