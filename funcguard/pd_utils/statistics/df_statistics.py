import pandas as pd
from typing import Union, List, Any, Dict, Tuple
from .mask_utils import build_single_mask


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
    
    def _get_true_mask(self) -> pd.Series:
        """获取全True的基础掩码，用于and逻辑"""
        if self._true_mask is None:
            self._true_mask = pd.Series([True] * self._length, index=self._index)
        return self._true_mask
    
    def _get_false_mask(self) -> pd.Series:
        """获取全False的基础掩码，用于or逻辑"""
        if self._false_mask is None:
            self._false_mask = pd.Series([False] * self._length, index=self._index)
        return self._false_mask
    
    def build_base_mask(self, conditions: List[Tuple], logic: str = "and") -> pd.Series:
        """
        构建基础查询条件掩码，复用基础Series对象
        
        参数：
        - conditions (List[Tuple]): 条件列表
        - logic (str): 逻辑操作类型，"and" 或 "or"
        
        返回：
        - pd.Series: 布尔掩码
        """
        if logic == "and":
            mask = self._get_true_mask().copy()  # 复制避免修改缓存
            operator_func = lambda m, c: m & c
        elif logic == "or":
            mask = self._get_false_mask().copy()  # 复制避免修改缓存
            operator_func = lambda m, c: m | c
        else:
            raise ValueError(f"不支持的逻辑操作类型: {logic}，支持 'and' 或 'or'")
        
        for condition in conditions:
            condition_mask = build_single_mask(self._df, condition)
            mask = operator_func(mask, condition_mask)
        
        return mask
    
    def count(self, conditions: Union[Tuple, List[Tuple]], logic: str = "and") -> int:
        """
        统计符合条件的行数
        
        参数：
        - conditions: 条件表达式
        - logic: 逻辑操作类型
        
        返回：
        - int: 符合条件的数量
        """
        # 单一条件
        if isinstance(conditions, tuple):
            mask = build_single_mask(self._df, conditions)
            return int(mask.sum())
        
        # 多条件
        mask = self.build_base_mask(conditions, logic)
        return int(mask.sum())
    
    def dataframe_info(self) -> Dict[str, Any]:
        """获取DataFrame的基本信息"""
        return {
            "shape": self._df.shape,
            "columns": list(self._df.columns),
            "dtypes": self._df.dtypes.to_dict(),
        }