import pandas as pd
from decimal import Decimal
from typing import Union, List, Dict, Any, Optional
from pandas import (
    Int64Dtype,
    Float64Dtype,
    StringDtype,
    BooleanDtype,
)  # pyright: ignore
from .json_utils import json_loads



# 数据类型映射常量
TYPE_MAPPING = {
    "int": Int64Dtype(),
    "float": Float64Dtype(),
    "str": StringDtype(),
    "bool": BooleanDtype(),
    "datetime": "datetime64[ns]",  # datetime使用字符串形式
}


def convert_numeric_series(series: pd.Series, decimal_places: Optional[int] = None) -> pd.Series:
    """
    将Series转换为数值类型，并自动检测应该使用 int 还是 float。

    流程：
    1. 先统一转换为 float64（确保所有值都是数值类型）
    2. 检测非空值中是否存在小数
    3. 如果没有小数则转换为 int64，否则保持 float64
    4. 如果指定了decimal_places且为float类型，则执行round操作

    参数：
    - series (pd.Series)：输入的Series
    - decimal_places (int, optional)：当结果为float类型时保留的小数位数，默认为None表示不限制

    返回：
    - pd.Series：转换后的Series
    """
    # 先统一转换为 float
    series = series.astype(float)

    # 检测是否存在小数
    non_null_values = series.dropna()
    if len(non_null_values) > 0:
        # 检查是否有任何值有小数部分
        has_decimal = any(non_null_values != non_null_values.round())
        if not has_decimal:
            # 没有小数，转换为 int64，并返回int64类型的Series
            return series.astype("int64")

    # 有小数或全是空值，保持 float64
    # 如果指定了decimal_places，对float类型执行round操作
    if decimal_places is not None:
        series = series.round(decimal_places)
    
    return series


def convert_columns(df: pd.DataFrame, columns: Dict[str, str], decimal_places: Optional[int] = None) -> pd.DataFrame:
    """
    转换DataFrame中指定列的数据类型。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (Dict[str, str])：
        要转换类型的字典，键为列名，值为目标数据类型。
        支持的数据类型：'int', 'float', 'str', 'bool', 'datetime'。
    - decimal_places (int, optional)：当转换为'float'类型时保留的小数位数，默认为None表示不限制

    返回：
    - pd.DataFrame：列类型转换后的DataFrame。
    """
    for column, target_type in columns.items():
        if column in df.columns and target_type in TYPE_MAPPING:
            try:
                if target_type == "datetime":
                    df[column] = pd.to_datetime(df[column], errors="coerce")
                elif target_type == "float":
                    df[column] = df[column].astype(
                        TYPE_MAPPING[target_type]
                    )  # pyright: ignore[reportArgumentType]
                    if decimal_places is not None:
                        df[column] = df[column].round(decimal_places)
                else:
                    df[column] = df[column].astype(
                        TYPE_MAPPING[target_type]
                    )  # pyright: ignore[reportArgumentType]
            except (ValueError, TypeError):
                # 如果转换失败，保持原类型
                pass
    return df


def convert_decimal(
    df: pd.DataFrame,
    columns: Union[List[str], Dict[str, str], None] = None,
    target_type: str = "int",
    decimal_places: Optional[int] = None,
) -> pd.DataFrame:
    """
    检测DataFrame中是否包含Decimal类型的字段，如果包含则转换为指定的数据类型。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (List[str], Dict[str, str], or None)：
        * 如果为None，则检测所有列
        * 如果为List[str]，则检测指定列，发现Decimal时转换为target_type指定的类型
        * 如果为Dict[str, str]，则键为列名，值为当发现Decimal时要转换的目标类型（支持'int'、'float'或'auto'）
    - target_type (str, optional)：当columns为列表时的默认转换类型，默认为'int'。
                                支持'int'、'float'或'auto'。
                                'auto'表示自动检测：先转为float，如果没有小数则转为int。
    - decimal_places (int, optional)：当target_type为'auto'或'float'时，保留的小数位数，默认为None表示不限制

    返回：
    - pd.DataFrame：转换后的DataFrame。
    """
    if columns is None:
        # 检测所有列
        target_columns = df.columns.tolist()
        column_types = {col: target_type for col in target_columns}
    elif isinstance(columns, list):
        # 检测指定列，使用默认类型
        target_columns = columns
        column_types = {col: target_type for col in target_columns}
    elif isinstance(columns, dict):
        # 使用字典指定的类型
        target_columns = list(columns.keys())
        column_types = columns

    # 验证target_type和字典中的类型是否有效
    valid_types = {"int", "float", "auto"}
    for col, target_type in column_types.items():
        if target_type not in valid_types:
            raise ValueError(
                f"无效的类型指定：{target_type}。支持的类型为：{valid_types}"
            )

    for column in target_columns:
        # 检查列是否存在且为object类型 (只有object类型列才可能包含Decimal)
        if column not in df.columns or df[column].dtype != object:
            continue
        # 检查列中的第一个非空值是否是Decimal类型
        first_non_null = df[column].first_valid_index()
        if first_non_null is None:
            continue
        if isinstance( df.at[first_non_null, column], Decimal ):  # pyright: ignore[reportArgumentType]
            # 根据指定的类型进行转换
            target_type = column_types[column]
            if target_type == "int":
                df[column] = df[column].astype(int)
            elif target_type == "float":
                df[column] = df[column].astype(float)
                if decimal_places is not None:
                    df[column] = df[column].round(decimal_places)
            elif target_type == "auto":
                df[column] = convert_numeric_series(df[column], decimal_places)

    return df


def load_json(
    df: pd.DataFrame,
    columns: List[str],
    empty_to_dict: bool = True,
) -> pd.DataFrame:
    """
    对DataFrame中指定的列执行json.loads操作，将JSON字符串转换为Python对象。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (List[str])：转换指定的多列
    - empty_to_dict (bool)：是否将空字符串转换为{}，默认为 True

    返回：
    - pd.DataFrame：JSON转换后的DataFrame。
    """

    for column in columns:

        # 使用独立的转换函数处理列中的每个值
        df[column] = df[column].apply(lambda x: json_loads(x, empty_to_dict))

    return df


def convert_datetime_str(
    df: pd.DataFrame,
    columns: List[str],
    include_time: bool = True,
    include_seconds: bool = True,
    fail_fill: Any = "",
    keep_original_on_fail: bool = False,
) -> pd.DataFrame:
    """
    将DataFrame中指定时间列转换为字符串类型。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (List[str])：要转换为datetime类型的列名列表。
    - include_time (bool)：是否保留时间部分，默认为 True（包含时间），为 False 时只保留日期。
    - include_seconds (bool)：当 include_time=True 时，是否包含秒，默认为 True。
    - fail_fill (Any)：转换失败时的填充值，默认空字符串。
    - keep_original_on_fail (bool)：转换失败时是否保留原值，默认为 False。

    返回：
    - pd.DataFrame：转换后的DataFrame。
    """
    if include_time:
        fmt = "%Y-%m-%d %H:%M:%S" if include_seconds else "%Y-%m-%d %H:%M"
    else:
        fmt = "%Y-%m-%d"

    for column in columns:
        if column not in df.columns:
            continue

        original = df[column]
        converted = pd.to_datetime(original, errors="coerce")
        formatted = converted.dt.strftime(fmt)
        fallback = original if keep_original_on_fail else fail_fill
        df[column] = formatted.where(~converted.isna(), fallback)
            
    return df


def convert_str_datetime(
    df: pd.DataFrame, columns: List[str]
) -> pd.DataFrame:
    """
    将DataFrame中指定字符串列转换为datetime类型。

    参数：
    - df (pd.DataFrame)：输入的DataFrame。
    - columns (List[str])：要转换为datetime类型的列名列表。

    返回：
    - pd.DataFrame：转换后的DataFrame。
    """
    def parse_datetime(value: str) -> Union[pd.Timestamp, str]:
        try:
            return pd.to_datetime(value)
        except (ValueError, TypeError):
            return value

    for column in columns:
        if column not in df.columns:
            continue

        df[column] = df[column].apply(parse_datetime)

    return df