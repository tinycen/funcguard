import re
from datetime import datetime
from typing import List
from urllib.parse import urlsplit, urlunsplit


def check_text(text: str, forbid_words: List[str]) -> bool:
    """
    检测文本中是否包含违禁词。

    :param text: 待检测文本
    :param forbid_words: 违禁词列表，为空则抛错
    :return: 命中任意违禁词返回 True，否则返回 False
    """
    if not forbid_words:
        raise ValueError("forbid_words is None")
    for word in forbid_words:
        if word.lower() in text.lower():
            return True
    return False


def clean_text(text: str, replacements: List[str]) -> str:
    """
    清理文本：去掉开头的中英文问号/冒号，并按 replacements 列表移除其中的子串。

    :param text: 待清理文本
    :param replacements: 需要移除的子串列表
    :return: 清理后的文本
    """
    if text and text[0] in {"?", ":", "：", "？"}:
        text = text[1:].strip()

    replacements = sorted(set(replacements), key=len, reverse=True)

    for replacement in replacements:
        regex = re.compile(re.escape(replacement), re.IGNORECASE)
        text = regex.sub("", text)
    return text.strip()


def clean_url(text: str) -> str:
    """
    清理 URL：去掉查询参数（?...）和锚点（#...）。

    例如 ``https://detail.1688.com/offer/6776924217.html?spm=a261y...&sk=order``
    清理后返回 ``https://detail.1688.com/offer/6776924217.html``。

    :param text: 待清理文本，作为 URL 解析
    :return: 去掉参数和锚点后的 URL
    """
    parts = urlsplit(text)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))


class TextCleaner:
    """
    文本年份归一化与清理工具。

    将文本中 2000~当前年份之间的年份统一替换为当前年份，
    并可按给定的替换词列表先做一次文案清理。
    """

    def __init__(self):
        self.current_year = datetime.now().year
        self.years_array = [str(year) for year in range(2000, self.current_year)]

    def normalize_year(self, text: str) -> str:
        """
        将文本中 2000~当前年份之间的年份统一替换为当前年份。

        :param text: 原始文本
        :return: 年份归一化后的文本
        """
        for year in self.years_array:
            text = re.sub(rf"\b{year}\b", str(self.current_year), text)
        return text

    def clean(self, text: str, replacements: List[str]) -> str:
        """
        先按 replacements 清理文本，再做年份归一化。

        :param text: 原始文本
        :param replacements: 需要移除的子串列表
        :return: 清理并年份归一化后的文本
        """
        if replacements:
            text = clean_text(text, replacements)
        return self.normalize_year(text)
