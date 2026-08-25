# 文本处理工具

FuncGuard 提供文本处理功能，用于违禁词检测、文本清理和年份归一化。

## check_text - 违禁词检测

检测文本中是否包含违禁词，命中任意违禁词返回 `True`，否则返回 `False`（大小写不敏感）。

```python
from funcguard import check_text

result = check_text("这是一个测试文本", ["测试", "禁止"])
print(result)  # True

result = check_text("正常的文本内容", ["测试", "禁止"])
print(result)  # False
```

**参数说明：**
- `text`: 待检测文本
- `forbid_words`: 违禁词列表，为空时抛出 `ValueError`

**返回值：**
- `bool`：命中任意违禁词返回 `True`，否则返回 `False`

---

## clean_text - 清理文本

清理文本：去掉开头的英文/中文问号、冒号，并按 `replacements` 列表移除其中的子串（大小写不敏感，按长度降序去重处理）。

```python
from funcguard import clean_text

result = clean_text("?：hello world", ["hello"])
print(result)  # world

result = clean_text("abcABC测试", ["abc", "abcABC"])
# 较长的 "abcABC" 优先被移除
print(result)  # 测试
```

**参数说明：**
- `text`: 待清理文本
- `replacements`: 需要移除的子串列表

**返回值：**
- `str`：清理并去除首尾空白后的文本

---

## clean_url - 清理 URL 参数

清理 URL：去掉查询参数（`?` 之后的部分）和锚点（`#` 之后的部分），保留协议、域名和路径。

```python
from funcguard import clean_url

result = clean_url("https://detail.1688.com/offer/677624217.html?spm=a261y.7663282.3002526303362591.2.32671cfas8Yzdd&sk=order")
print(result)  # https://detail.1688.com/offer/677624217.html
```

**参数说明：**
- `text`: 待清理文本，将作为 URL 解析

**返回值：**
- `str`：去掉查询参数和锚点后的 URL

---

## TextCleaner - 文本年份归一化与清理

将文本中 2000~当前年份之间的年份统一替换为当前年份，并可按替换词列表先做一次文案清理。

### normalize_year - 年份归一化

将文本中 2000~当前年份之间、独立的年份数字（4 位且前后有单词边界）统一替换为当前年份。

```python
from funcguard import TextCleaner

cleaner = TextCleaner()
result = cleaner.normalize_year("发布于 2023 年")
print(result)  # 发布于 {当前年份} 年（如 2026 年）
```

**参数说明：**
- `text`: 原始文本

**返回值：**
- `str`：年份归一化后的文本

### clean - 清理并归一化

先按 `replacements` 清理文本，再做年份归一化。

```python
from funcguard import TextCleaner

cleaner = TextCleaner()
result = cleaner.clean("?：2023 年发布的 old 版本", ["old"])
print(result)  # 版本名 文本，其中 2023 会被替换为当前年份
```

**参数说明：**
- `text`: 原始文本
- `replacements`: 需要移除的子串列表

**返回值：**
- `str`：清理并年份归一化后的文本