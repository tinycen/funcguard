# 打印工具

FuncGuard 提供终端格式化打印工具，位于 `funcguard/printer.py`。
所有函数输出均带 `flush=True`，在管道/重定向场景下实时可见、进程异常退出不丢。

## print_progress - 进度条

打印进度条，显示当前进度。

```python
from funcguard import print_progress

for i in range(101):
    print_progress(i, 100, "处理中")
```

**参数说明：**
- `idx`: 当前索引（从 0 开始）
- `total`: 总数量（`<= 0` 时打印警告并直接返回）
- `message`: 额外消息，默认为空字符串

**输出形态（自动感知终端）：**

| 环境 | 行为 |
|------|------|
| 终端（tty） | `\r` 原地覆盖刷新同一行，`\033[K` 清行尾防止残留 |
| 非终端（管道/文件/CI） | 降级为按 **10% 步进**的换行输出，100% 必打；`idx` 回到 0% 时重置步进基准（同一进程可连续使用多个进度条） |

其他特性：
- 百分比钳制在 0~100：`print_progress(15, 10)` 显示 `100% (15/10)`，条体不溢出 50 字符
- 进度条固定 50 字符宽，`█` 表示已完成部分，`-` 表示未完成部分

subprocess 捕获时的行为详见 [subprocess_output.md](./subprocess_output.md)。

---

## print_title - 标题打印

打印带分隔符的标题，格式如 `=== 初始化分类器 ===`。

```python
from funcguard import print_title

print_title("初始化分类器")                            # === 初始化分类器 ===
print_title("训练完成", separator_char="*", padding_length=2)  # ** 训练完成 **
```

**参数说明：**
- `title`: 标题内容
- `separator_char`: 分隔符字符，默认 `"="`
- `padding_length`: 标题两侧的分隔符数量，默认 `3`

---

## print_line - 分隔线

打印分隔线，用于分隔不同的打印块。

```python
from funcguard import print_line

print_line()        # 默认 40 个 '-'
print_line("*", 30) # 30 个 '*'
```

**参数说明：**
- `separator_char`: 分隔符字符，默认 `"-"`
- `separator_length`: 分隔符长度，默认 `40`

---

## print_block - 块打印

使用分隔符打印标题和内容，便于查看。

```python
from funcguard import print_block

print_block("用户信息", {"name": "张三", "age": 25})
```

**参数说明：**
- `title`: 标题（为空时只打印内容）
- `content`: 打印的内容
- `separator_char`: 分隔符字符，默认 `"-"`
- `separator_length`: 分隔符长度，默认 `40`
