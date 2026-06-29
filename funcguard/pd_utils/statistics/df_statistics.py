import pandas as pd
from collections.abc import Mapping
from typing import Any, Literal
from .mask_utils import build_single_mask as _original_build_single_mask, build_base_mask as _original_build_base_mask, combine_masks
from .count_utils import count as _original_count, value_counts as _original_value_counts
from .agg_utils import group_agg as _original_group_agg



class DataFrameStatistics:
    """
    DataFrame统计分析类，用于复用pd.Series对象，优化多次统计操作的性能

    主要优化点：
    1. 缓存基础掩码，避免重复创建pd.Series([True] * len(df))
    2. 复用相同DataFrame的索引，减少内存分配
    3. 提供批量统计功能，减少函数调用开销
    """

    def __init__(self, df: pd.DataFrame):
        """
        初始化统计分析器

        参数：
        - df (pd.DataFrame): 要统计的DataFrame
        """
        self._df = df
        self._index = df.index
        self._length = len(df)

        # 缓存基础掩码，避免重复创建
        self._true_mask = None
        self._false_mask = None
        self._reset_base_masks()


    # 重置 true_mask 和 false_mask
    def _reset_base_masks(self):
        """重置基础掩码为全True和全False"""
        self._true_mask = pd.Series([True] * len(self._df), index=self._df.index)
        self._false_mask = pd.Series([False] * len(self._df), index=self._df.index)

    def _ensure_masks_valid(self):
        """如果 DataFrame 发生变化，重新生成基础掩码"""
        if self._true_mask is not None and len(self._true_mask) != len(self._df):
            self._reset_base_masks()

    def combine_masks(self, masks: list[pd.Series], logic: str = "and") -> pd.Series:
        """
        合并多个布尔掩码，支持复杂的嵌套逻辑组合（委托给模块级 combine_masks 函数）
        """
        return combine_masks(masks, logic)


    def build_base_mask(self, conditions: list[tuple], logic: str = "and",
                       true_mask: pd.Series | None = None,
                       false_mask: pd.Series | None = None) -> pd.Series:
        """
        构建基础查询条件掩码，自动使用内部掩码参数
        
        参数：
        - conditions (List[Tuple])：条件列表，每个元组包含(列名, 运算符, 值)
        - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"
        - true_mask (pd.Series)：初始True掩码，默认为None（使用内部缓存）
        - false_mask (pd.Series)：初始False掩码，默认为None（使用内部缓存）

        返回：
        - pd.Series：布尔掩码，True表示符合条件的行
        """
        self._ensure_masks_valid()
        # 如果没有提供外部掩码，使用内部缓存的掩码
        if true_mask is None:
            true_mask = self._true_mask
        if false_mask is None:
            false_mask = self._false_mask
        return _original_build_base_mask(self._df, conditions, logic, true_mask, false_mask)


    def build_single_mask(self, condition: tuple) -> pd.Series:
        """
        构建单个掩码，用于简单条件判断，自动使用内部DataFrame

        参数：
        - condition (Tuple)：条件元组，包含(列名, 运算符, 值)

        返回：
        - pd.Series：布尔掩码，True表示符合条件的行
            **注意**：此Series是通过原生pandas表达式(df[col] > value)直接返回，
            无额外内存分配和位运算，性能最优。适用于简单单一条件场景。
        """
        return _original_build_single_mask(self._df, condition)


    def count(self, conditions: tuple | list[tuple], logic: str = "and",
             true_mask: pd.Series | None = None,
             false_mask: pd.Series | None = None) -> int:
        """
        统计DataFrame中符合条件的非空值数量，自动使用内部掩码参数

        参数：
        - conditions (Union[Tuple, List[Tuple]])：符合条件的表达式
        - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"
        - true_mask (pd.Series)：初始True掩码，默认为None（使用内部缓存）
        - false_mask (pd.Series)：初始False掩码，默认为None（使用内部缓存）

        返回：
        - int：符合条件的数量
        """
        self._ensure_masks_valid()
        # 如果没有提供外部掩码，使用内部缓存的掩码
        if true_mask is None:
            true_mask = self._true_mask
        if false_mask is None:
            false_mask = self._false_mask
        return _original_count(self._df, conditions, logic, true_mask, false_mask)


    def value_counts(
        self,
        column: str,
        mode: str = "count",
        sort: str | None = None,
        dropna: bool = True,
        conditions: tuple | list[tuple] | None = None,
        logic: str = "and",
        true_mask: pd.Series | None = None,
        false_mask: pd.Series | None = None,
        return_type: Literal["dict", "df", "series"] = "dict"
    ) -> Mapping[Any, int | float] | pd.DataFrame | pd.Series:
        """
        统计指定列中不同值的计数数据，自动使用内部掩码参数

        参数：
        - column (str)：要统计的列名
        - mode (str)：统计模式，"count" 表示计数，"percent" 表示百分比，默认为 "count"
        - sort (Optional[str])：排序方式，"asc" 表示升序，"desc" 表示降序，
            默认为None表示不排序
        - dropna (bool)：是否排除空值，默认为True
        - conditions (Optional[Union[Tuple, List[Tuple]]])：可选的过滤条件
        - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"
        - true_mask (pd.Series)：初始True掩码，默认为None（使用内部缓存）
        - false_mask (pd.Series)：初始False掩码，默认为None（使用内部缓存）
        - return_type (str)：返回类型，支持 "dict"（字典）、"df"（DataFrame）和 "series"（Series），
            默认为 "dict"。

        返回：
        - Union[Mapping[Any, Union[int, float]], pd.DataFrame, pd.Series]：以值为键，计数/百分比为值的字典、DataFrame或Series

        示例：
            >>> stats.value_counts("status")
            {'active': 150, 'inactive': 50, 'pending': 20}
            >>> stats.value_counts("status", mode="percent")
            {'active': 0.6818, 'inactive': 0.2273, 'pending': 0.0909}
            >>> stats.value_counts("status", sort="desc")
            {'active': 150, 'inactive': 50, 'pending': 20}
            >>> stats.value_counts("status", sort="asc")
            {'pending': 20, 'inactive': 50, 'active': 150}
            >>> stats.value_counts("status", conditions=[("age", ">", 18)])
            {'active': 120, 'inactive': 30}
        """
        self._ensure_masks_valid()
        # 如果没有提供外部掩码，使用内部缓存的掩码
        if true_mask is None:
            true_mask = self._true_mask
        if false_mask is None:
            false_mask = self._false_mask
        return _original_value_counts(
            self._df, column, mode, sort, dropna,
            conditions, logic, true_mask, false_mask, return_type
        )


    def group_agg(
        self,
        group_col: str,
        agg_col: str,
        agg_func: str = "sum",
        sort: str | None = None,
        conditions: tuple | list[tuple] | None = None,
        logic: str = "and",
        true_mask: pd.Series | None = None,
        false_mask: pd.Series | None = None,
        return_type: Literal["dict", "df", "series"] = "dict"
    ) -> dict[Any, int | float] | pd.DataFrame | pd.Series:
        """
        按指定列分组，对另一列进行聚合统计，自动使用内部掩码参数

        参数：
        - group_col (str)：分组列名（如A列）
        - agg_col (str)：聚合列名（如B列）
        - agg_func (str)：聚合函数，支持 "sum"、"mean"、"max"、"min"、"count"、"median"、"std"、"var"，
            默认为 "sum"
        - sort (Optional[str])：排序方式，"asc" 表示升序，"desc" 表示降序，
            默认为None表示按分组列的原始顺序
        - conditions (Optional[Union[Tuple, List[Tuple]]])：可选的过滤条件
        - logic (str)：逻辑操作类型，"and" 或 "or"，默认为 "and"
        - true_mask (pd.Series)：初始True掩码，默认为None（使用内部缓存）
        - false_mask (pd.Series)：初始False掩码，默认为None（使用内部缓存）
        - return_type (str)：返回类型，支持 "dict"（字典）、"df"（DataFrame）和 "series"（Series），
            默认为 "dict"。

        返回：
        - Union[Dict[Any, Union[int, float]], pd.DataFrame, pd.Series]：以分组值为键，聚合结果为值的字典、DataFrame或Series

        示例：
            >>> stats.group_agg("category", "amount", "sum")
            {'A': 1000, 'B': 2000, 'C': 1500}
            >>> stats.group_agg("category", "amount", "mean")
            {'A': 100.0, 'B': 200.0, 'C': 150.0}
            >>> stats.group_agg("category", "amount", "sum", sort="desc")
            {'B': 2000, 'C': 1500, 'A': 1000}
        """
        self._ensure_masks_valid()
        # 如果没有提供外部掩码，使用内部缓存的掩码
        if true_mask is None:
            true_mask = self._true_mask
        if false_mask is None:
            false_mask = self._false_mask
        return _original_group_agg(
            self._df, group_col, agg_col, agg_func, sort,
            conditions, logic, true_mask, false_mask, return_type
        )


    def dataframe_info(self) -> dict[str, Any]:
        """获取DataFrame的基本信息"""
        return {
            "shape": self._df.shape,
            "columns": list(self._df.columns),
            "dtypes": self._df.dtypes.to_dict(),
        }
