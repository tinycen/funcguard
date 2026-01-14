def format_difference(old_value: int | float, new_value: int | float, add_space: bool = False) -> str:
    """
    格式化两个数值的差异。
    
    Args:
        old_value: 原始值
        new_value: 新值
        add_space: 是否在差异符号前添加空格，默认为 False
    
    Returns:
        str: 格式化后的差异字符串，如果差异为0则返回空字符串
    """
    difference = new_value - old_value
    if difference == 0:
        return ""
    
    prefix = " " if add_space else ""
    
    # 检查差异值是否为整数（尾数为0的浮点数）
    if difference == int(difference):
        difference = int(difference)
    
    if difference > 0:
        return f"{prefix}+{difference}"
    if difference < 0:
        return f"{prefix}-{abs(difference)}"
    return str(difference)