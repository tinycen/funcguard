import pandas as pd
from typing import  Any, Dict
from .mask_utils import build_single_mask, build_base_mask, combine_masks
from .count_utils import count



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
        self.build_base_mask = build_base_mask
        self.combine_masks = combine_masks
        self.count = count


    # 重置 true_mask 和 false_mask
    def _reset_base_masks(self):
        """重置基础掩码为全True和全False"""
        self._true_mask = pd.Series([True] * self._length, index=self._index)
        self._false_mask = pd.Series([False] * self._length, index=self._index)


    def dataframe_info(self) -> Dict[str, Any]:
        """获取DataFrame的基本信息"""
        return {
            "shape": self._df.shape,
            "columns": list(self._df.columns),
            "dtypes": self._df.dtypes.to_dict(),
        }
