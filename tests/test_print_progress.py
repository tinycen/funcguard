"""
测试 print_progress 在 subprocess 中能否正常打印进度条。

验证点：
1. 真实 .py 脚本文件被 subprocess 执行时，进度条能正常输出
2. 进度条格式正确（百分比、进度条填充字符、计数器）
3. 包含 \\r 回车符用于行内刷新
4. 最终输出包含 100% 完成状态
5. 输出是"边跑边吐"的（flush=True 生效），而不是进程退出时一次性刷出

设计说明：
- 使用 sys.path.insert 直接定位 printer 模块，避免触发 funcguard 包 __init__.py
  中 requests 等第三方依赖的导入。
- 统一给子进程设置 PYTHONIOENCODING=utf-8，避免非 UTF-8 locale（如中文 Windows
  默认 GBK）下父进程解码失败或出现乱码。
- flush 是否生效只能用"流式读取"验证：capture_output 会在进程退出时拿到全部内容，
  无论有没有 flush 都能通过，属于假通过。
"""
import contextlib
import io
import os
import subprocess
import sys
import tempfile
import textwrap
import time


# 项目根目录与 printer 模块所在目录
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FUNCGUARD_DIR = os.path.join(PROJECT_DIR, "funcguard")

# 固定子进程 IO 编码，保证父进程可以安全地按 utf-8 解码
CHILD_ENV = dict(os.environ, PYTHONIOENCODING="utf-8")

# 子进程脚本头部：注入模块搜索路径，使 printer 可被直接导入
_SETUP_LINE = f"import sys; sys.path.insert(0, r'{FUNCGUARD_DIR}');"


@contextlib.contextmanager
def _temp_script(source: str):
    """把源码写成一个真实的 .py 临时脚本文件，退出时清理。

    :param source: 脚本正文（会被 textwrap.dedent 处理）
    """
    fd, path = tempfile.mkstemp(suffix=".py", prefix="test_progress_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("# -*- coding: utf-8 -*-\n")
            f.write(_SETUP_LINE + "\n")
            f.write(textwrap.dedent(source))
        yield path
    finally:
        # Windows 下文件可能仍被占用，清理失败不影响测试结果
        with contextlib.suppress(OSError):
            os.remove(path)


def _run_subprocess_script(script: str, raw: bool = False) -> subprocess.CompletedProcess:
    """以 `-c` 内联代码方式在子进程中执行并捕获输出。

    :param script: 要执行的 Python 代码
    :param raw: 为 True 时使用二进制流捕获，保留 \\r 原字符（不启用通用换行转换）
    """
    code = _SETUP_LINE + " " + textwrap.dedent(script)

    if raw:
        # 二进制模式：不启用通用换行转换，保留原始 \\r 字符
        proc = subprocess.run(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=CHILD_ENV,
            timeout=30,
        )
        # 用 newline='' 包装：不把 \\r 转成 \\n，保留原始回车符
        stdout_text = io.TextIOWrapper(
            io.BytesIO(proc.stdout), encoding="utf-8", newline=""
        ).read()
        stderr_text = io.TextIOWrapper(
            io.BytesIO(proc.stderr), encoding="utf-8", newline=""
        ).read()
        return subprocess.CompletedProcess(
            args=proc.args,
            returncode=proc.returncode,
            stdout=stdout_text,
            stderr=stderr_text,
        )
    else:
        return subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=CHILD_ENV,
            timeout=30,
        )


def _run_script_file(script: str, raw: bool = False) -> subprocess.CompletedProcess:
    """把代码写成真实 .py 文件后用 subprocess 执行并捕获输出。

    与 `-c` 内联方式的区别：走的是真实脚本文件路径，更贴近实际使用场景
    （如 `python xxx.py` 被调度脚本 / CI 调用）。

    :param script: 要执行的 Python 代码
    :param raw: 为 True 时保留原始 \\r 字符
    """
    with _temp_script(script) as path:
        if raw:
            proc = subprocess.run(
                [sys.executable, path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=CHILD_ENV,
                timeout=30,
            )
            stdout_text = io.TextIOWrapper(
                io.BytesIO(proc.stdout), encoding="utf-8", newline=""
            ).read()
            stderr_text = io.TextIOWrapper(
                io.BytesIO(proc.stderr), encoding="utf-8", newline=""
            ).read()
            return subprocess.CompletedProcess(
                args=proc.args,
                returncode=proc.returncode,
                stdout=stdout_text,
                stderr=stderr_text,
            )
        else:
            return subprocess.run(
                [sys.executable, path],
                capture_output=True,
                text=True,
                encoding="utf-8",
                env=CHILD_ENV,
                timeout=30,
            )


def _stream_script_file(
    script: str, timeout: float = 30.0
) -> tuple[str, list[float], int]:
    """以流式方式运行真实 .py 脚本，逐字节读取并记录每一帧的到达时刻。

    这是验证 flush=True 是否真正生效的唯一可靠手段：
    - 若输出被缓冲，所有进度帧会在进程退出时"一次性"到达，帧间距几乎为 0；
    - 若 flush 生效，各帧会随 sleep 间隔陆续到达。

    用"帧到达时间跨度"而不是"首字节到达时进程是否存活"来判定，是因为后者存在竞态：
    子进程退出瞬间刷数据，父进程 poll() 时它可能还没完全退出，会误判为实时。

    :param script: 要执行的 Python 代码
    :param timeout: 读取超时（秒）
    :return: (输出文本, 每个进度帧的到达时刻, 退出码)
    """
    with _temp_script(script) as path:
        proc = subprocess.Popen(
            [sys.executable, path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=CHILD_ENV,
            bufsize=0,  # 无缓冲：read(1) 有数据就立刻返回，便于记录到达时刻
        )

        chunks: list[bytes] = []
        frame_times: list[float] = []  # 每遇到一个 \\r（新一帧开始）就记一次时刻
        deadline = time.monotonic() + timeout
        stderr_data = b""

        try:
            while time.monotonic() < deadline:
                chunk = proc.stdout.read(1)  # 阻塞直到读到 1 字节或 EOF
                if not chunk:
                    break
                if chunk == b"\r":
                    frame_times.append(time.monotonic())
                chunks.append(chunk)
        finally:
            if proc.stdout:
                proc.stdout.close()
            if proc.stderr:
                stderr_data = proc.stderr.read()
                proc.stderr.close()
            if proc.poll() is None:
                proc.kill()
            proc.wait(timeout=10)

    stdout_text = b"".join(chunks).decode("utf-8", errors="replace")
    if proc.returncode != 0 and stderr_data:
        stdout_text += "\n[stderr] " + stderr_data.decode("utf-8", errors="replace")
    return stdout_text, frame_times, proc.returncode


def test_print_progress_basic_output_in_subprocess():
    """验证 subprocess 中调用 print_progress 能正常输出"""
    script = """
        from printer import print_progress
        print_progress(5, 10)
    """
    result = _run_subprocess_script(script)
    assert result.returncode == 0, f"脚本执行失败: {result.stderr}"
    # 输出应包含进度条关键元素
    assert "50%" in result.stdout, f"期望输出包含 50%，实际输出: {repr(result.stdout)}"
    assert "(5/10)" in result.stdout, f"期望输出包含 (5/10)，实际输出: {repr(result.stdout)}"
    assert "|" in result.stdout, f"期望输出包含进度条分隔符 |，实际输出: {repr(result.stdout)}"


def test_print_progress_contains_carriage_return():
    """验证输出中包含回车符（行内刷新需要）。

    注意：subprocess.run 的 text=True 模式会启用通用换行转换（\\r -> \\n），
    因此需用 raw=True 在二进制模式下捕获以保留原始 \\r 字符。
    """
    script = """
        from printer import print_progress
        print_progress(0, 5)
        print_progress(3, 5)
        print_progress(5, 5)
    """
    result = _run_subprocess_script(script, raw=True)
    assert result.returncode == 0, f"脚本执行失败: {result.stderr}"

    cr = "\r"  # 先取成变量，避免 f-string 表达式内出现反斜杠（Python < 3.12 会 SyntaxError）
    cr_count = result.stdout.count(cr)
    assert cr in result.stdout, f"期望输出包含回车符，实际输出: {repr(result.stdout)}"
    assert cr_count == 3, (
        f"期望输出包含 3 个回车符（与调用次数一致），实际: {cr_count} 个，"
        f"输出: {repr(result.stdout)}"
    )


def test_print_progress_full_cycle_in_subprocess():
    """验证完整的进度循环在 subprocess 中的输出"""
    script = """
        import time
        from printer import print_progress
        total = 10
        for i in range(total + 1):
            print_progress(i, total, message="处理中...")
            if i < total:
                time.sleep(0.01)
    """
    result = _run_subprocess_script(script)
    assert result.returncode == 0, f"脚本执行失败: {result.stderr}"
    # 最终输出应包含 100%
    assert "100%" in result.stdout, f"期望输出包含 100%，实际输出: {repr(result.stdout)}"
    # 应包含完整的计数信息
    assert "(10/10)" in result.stdout, f"期望输出包含 (10/10)，实际输出: {repr(result.stdout)}"


def test_print_progress_bar_characters():
    """验证进度条使用了正确的填充字符"""
    script = """
        from printer import print_progress
        print_progress(10, 10)
    """
    result = _run_subprocess_script(script)
    assert result.returncode == 0, f"脚本执行失败: {result.stderr}"
    # 100% 时应全部用 '█' 填充
    progress_line = result.stdout
    assert "█" in progress_line, f"期望输出包含进度条填充字符 '█'，实际输出: {repr(progress_line)}"


def test_print_progress_zero_percent():
    """验证 0% 进度的输出"""
    script = """
        from printer import print_progress
        print_progress(0, 100)
    """
    result = _run_subprocess_script(script)
    assert result.returncode == 0, f"脚本执行失败: {result.stderr}"
    assert "0%" in result.stdout, f"期望输出包含 0%，实际输出: {repr(result.stdout)}"
    assert "(0/100)" in result.stdout, f"期望输出包含 (0/100)，实际输出: {repr(result.stdout)}"


def test_print_progress_with_message():
    """验证自定义消息的输出"""
    script = """
        from printer import print_progress
        print_progress(5, 10, message="正在下载文件...")
    """
    result = _run_subprocess_script(script)
    assert result.returncode == 0, f"脚本执行失败: {result.stderr}"
    assert "正在下载文件..." in result.stdout, f"期望输出包含自定义消息，实际输出: {repr(result.stdout)}"


def test_print_progress_invalid_total():
    """验证 total 为 0 或负数时的处理"""
    script = """
        from printer import print_progress
        print_progress(5, 0)
    """
    result = _run_subprocess_script(script)
    assert result.returncode == 0, f"脚本执行失败: {result.stderr}"
    assert "警告" in result.stdout, f"期望输出包含警告信息，实际输出: {repr(result.stdout)}"


# ---------------- 真实 .py 脚本文件相关测试 ----------------

def test_print_progress_in_real_py_file():
    """验证进度条在真实 .py 脚本文件中能正常打印（而非 -c 内联代码）"""
    script = """
        import time
        from printer import print_progress

        total = 10
        for i in range(total + 1):
            print_progress(i, total, message="处理中...")
            time.sleep(0.01)
        print()  # 结束时换行，避免最后一行被 shell 提示符覆盖
    """
    result = _run_script_file(script)
    assert result.returncode == 0, f"脚本执行失败: {result.stderr}"
    assert "100%" in result.stdout, f"期望输出包含 100%，实际输出: {repr(result.stdout)}"
    assert "(10/10)" in result.stdout, f"期望输出包含 (10/10)，实际输出: {repr(result.stdout)}"
    assert "█" in result.stdout, f"期望输出包含进度条填充字符，实际输出: {repr(result.stdout)}"


def test_print_progress_in_real_py_file_keeps_carriage_return():
    """真实 .py 脚本输出中同样保留 \\r 回车符（行内刷新的前提）"""
    script = """
        from printer import print_progress
        print_progress(0, 4)
        print_progress(2, 4)
        print_progress(4, 4)
    """
    result = _run_script_file(script, raw=True)
    assert result.returncode == 0, f"脚本执行失败: {result.stderr}"

    cr = "\r"
    cr_count = result.stdout.count(cr)
    assert cr_count == 3, (
        f"期望输出包含 3 个回车符（与调用次数一致），实际: {cr_count} 个，"
        f"输出: {repr(result.stdout)}"
    )


def test_print_progress_streams_in_realtime():
    """验证进度条是边跑边输出的（flush=True 真正生效）。

    判定依据是"各帧到达的时间跨度"：若输出被缓冲，所有帧会在进程退出时一次性
    到达，跨度接近 0。实测（Windows / Python 3.13）：
      有 flush -> 首字节 0.61s 到达；无 flush -> 2.16s（等进程结束）。
    """
    script = """
        import time
        from printer import print_progress
        for i in range(5):
            print_progress(i, 4)
            time.sleep(0.4)  # 拉开间隔：5 帧理论跨度约 1.6s
    """
    stdout, frame_times, returncode = _stream_script_file(script)
    assert returncode == 0, f"脚本执行失败: {stdout}"
    assert len(frame_times) == 5, (
        f"期望收到 5 个进度帧，实际收到 {len(frame_times)} 个，输出: {repr(stdout)}"
    )

    spread = frame_times[-1] - frame_times[0]
    assert spread > 1.0, (
        f"进度帧几乎同时到达（跨度仅 {spread:.3f}s），说明输出被缓冲到进程退出才刷出，"
        f"flush=True 未生效"
    )
    assert "100%" in stdout, f"期望流式输出包含 100%，实际输出: {repr(stdout)}"


def test_print_progress_stream_frames_split_by_carriage_return():
    """验证流式输出可以按 \\r 切帧，每一帧都是一条完整进度"""
    script = """
        import time
        from printer import print_progress
        for i in range(4):
            print_progress(i, 3, message="处理中...")
            time.sleep(0.1)
    """
    stdout, _, returncode = _stream_script_file(script)
    assert returncode == 0, f"脚本执行失败: {stdout}"

    frames = [frame for frame in stdout.split("\r") if frame.strip()]
    assert len(frames) == 4, f"期望 4 帧进度（与调用次数一致），实际 {len(frames)} 帧: {repr(stdout)}"
    assert "0%" in frames[0], f"首帧应为 0%，实际: {repr(frames[0])}"
    assert "100%" in frames[-1], f"末帧应为 100%，实际: {repr(frames[-1])}"


if __name__ == "__main__":
    print("=" * 60)
    print("测试 print_progress 在 subprocess 中的打印功能")
    print("=" * 60)

    tests = [
        ("基本输出", test_print_progress_basic_output_in_subprocess),
        ("回车符检查", test_print_progress_contains_carriage_return),
        ("完整进度循环", test_print_progress_full_cycle_in_subprocess),
        ("进度条字符", test_print_progress_bar_characters),
        ("0% 进度", test_print_progress_zero_percent),
        ("自定义消息", test_print_progress_with_message),
        ("非法 total 值", test_print_progress_invalid_total),
        ("真实 .py 脚本", test_print_progress_in_real_py_file),
        ("真实 .py 脚本保留回车符", test_print_progress_in_real_py_file_keeps_carriage_return),
        ("流式实时输出(flush)", test_print_progress_streams_in_realtime),
        ("流式按回车符切帧", test_print_progress_stream_frames_split_by_carriage_return),
    ]

    passed = 0
    failed = 0
    for name, test_func in tests:
        try:
            test_func()
            print(f"  ✓ {name}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {name}: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ {name}: 异常 - {type(e).__name__}: {e}")
            failed += 1

    print("-" * 60)
    print(f"结果: {passed} 通过, {failed} 失败")
    sys.exit(1 if failed else 0)
