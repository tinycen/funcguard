def format_difference(
    old_value: int | float,
    new_value: int | float,
    decimal_places: int = 2,
    add_space: bool = False,
) -> str:
    """
    格式化两个数值的差异。

    Args:
        old_value: 原始值
        new_value: 新值
        decimal_places: 小数位数，默认为 2
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
    else:
        # 对浮点数进行四舍五入，控制小数位数
        difference = round(difference, decimal_places)

    # Python 的浮点数表示和 f-string 格式化会自动去掉无意义的末尾 0
    # 例如：round(1.10, 2) 得到 1.1，最终输出为 "+1.1" 而不是 "+1.10"
    if difference > 0:
        return f"{prefix}+{difference}"
    if difference < 0:
        return f"{prefix}-{abs(difference)}"
    return str(difference)
