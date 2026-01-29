import pandas as pd
from typing import  Any, Dict, List, Tuple, Union, Optional
from .mask_utils import build_single_mask, build_base_mask as _original_build_base_mask, combine_masks
from .count_utils import count as _original_count



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

        # 方法继承
        self.build_single_mask = build_single_mask
        self.combine_masks = combine_masks


    # 重置 true_mask 和 false_mask
    def _reset_base_masks(self):
        """重置基础掩码为全True和全False"""
        self._true_mask = pd.Series([True] * self._length, index=self._index)
        self._false_mask = pd.Series([False] * self._length, index=self._index)

    def build_base_mask(self, conditions: List[Tuple], logic: str = "and", 
                       true_mask: Optional[pd.Series] = None, 
                       false_mask: Optional[pd.Series] = None) -> pd.Series:
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
        # 如果没有提供外部掩码，使用内部缓存的掩码
        if true_mask is None:
            true_mask = self._true_mask
        if false_mask is None:
            false_mask = self._false_mask
        return _original_build_base_mask(self._df, conditions, logic, true_mask, false_mask)

    def count(self, conditions: Union[Tuple, List[Tuple]], logic: str = "and",
             true_mask: Optional[pd.Series] = None, 
             false_mask: Optional[pd.Series] = None) -> int:
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
        # 如果没有提供外部掩码，使用内部缓存的掩码
        if true_mask is None:
            true_mask = self._true_mask
        if false_mask is None:
            false_mask = self._false_mask
        return _original_count(self._df, conditions, logic, true_mask, false_mask)


    def dataframe_info(self) -> Dict[str, Any]:
        """获取DataFrame的基本信息"""
        return {
            "shape": self._df.shape,
            "columns": list(self._df.columns),
            "dtypes": self._df.dtypes.to_dict(),
        }
