from typing import Any

# 打印带等号的标题（如：=== 初始化分类器 ===）
def print_title(title: str, separator_char: str = "=", padding_length: int = 3) -> None:
    """
    打印带分隔符的标题，格式如：=== 初始化分类器 ===
    
    :param title: 标题内容
    :param separator_char: 分隔符字符，默认为'='
    :param padding_length: 标题两侧的分隔符数量，默认为3
    """
    separator = separator_char * padding_length
    print(f"{separator} {title} {separator}")


# 打印分隔线
def print_line(separator_char: str = "-", separator_length: int = 40) -> None:
    """
    打印分隔线，用于分隔不同的打印块

    :param separator_char: 分隔符字符，默认为'-'
    :param separator_length: 分隔符长度，默认为40
    """
    separator = separator_char * separator_length
    print(separator)


# 块打印
def print_block(title: str, content: Any, separator_char: str = "-", separator_length: int = 40) -> None:
    """
    使用分隔符打印标题和内容，便于查看

    :param title: 标题
    :param content: 打印的内容
    :param separator_char: 分隔符字符，默认为'-'
    :param separator_length: 分隔符长度，默认为40
    """
    print_line(separator_char, separator_length)

    if title:
        print(f"{title} :")
    print(content)

    print_line(separator_char, separator_length)
    # print()  # 添加一个空行便于阅读