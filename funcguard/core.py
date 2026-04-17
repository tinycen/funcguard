import time
from concurrent.futures import ThreadPoolExecutor , TimeoutError


class FuncguardTimeoutError(Exception):
    """
    funcguard库专用的超时异常类。

    为了避免与concurrent.futures.TimeoutError和Python内置TimeoutError的命名冲突，
    特定义此异常类来明确表示这是funcguard库抛出的函数执行超时异常。
    这样用户可以清晰地区分异常来源，并进行针对性的异常处理。
    """
    pass


# 计算函数运行时间
def timeout_handler( func, args = (), kwargs = None, execution_timeout = 90 ):
    """
    使用 ThreadPoolExecutor 实现超时控制。

    :param func: 需要执行的目标函数
    :param args: 目标函数的位置参数，默认为空元组
    :param kwargs: 目标函数的关键字参数，默认为 None
    :param execution_timeout: 函数执行的超时时间，单位为秒，默认为 90 秒
    :return: 目标函数的返回值
    """
    if kwargs is None:
        kwargs = { }

    with ThreadPoolExecutor( max_workers = 1 ) as executor:
        future = executor.submit( func, *args, **kwargs )
        try:
            return future.result( timeout = execution_timeout )
        except TimeoutError:
            error_message = f"TimeoutError：函数 {func.__name__} 执行时间超过 {execution_timeout} 秒"
            # print( error_message )
            raise FuncguardTimeoutError( error_message )


# 重试函数
def retry_function( func , max_retries = 5 , execute_timeout = 90 , task_name = "" , *args , **kwargs ) :
    """
    重试函数的通用封装。
    :param func: 需要重试的函数
    :param max_retries: 最大重试次数
    :param execute_timeout: 执行超时时间
    :param task_name: 任务名称，用于打印日志
    :param args: func的位置参数
    :param kwargs: func的关键字参数
    :return: func的返回值
    """
    retry_count = 0
    current_timeout = execute_timeout  # 初始化当前超时时间为传入的execute_timeout

    # 检查原始kwargs中是否包含timeout参数
    original_timeout = kwargs.get( 'timeout' , 0 )

    if current_timeout < original_timeout :
        current_timeout = original_timeout + 30

    last_exception = None
    while retry_count < max_retries :
        try :
            result = timeout_handler( func , args = args , kwargs = kwargs , execution_timeout = current_timeout )
            return result  # 如果调用成功，则返回结果

        except Exception as e :
            last_exception = e
            retry_count += 1
            print( e )
            if "TimeoutError" in str( e ) :
                # 计划延长的时间
                extend_time = 30 * retry_count

                # 增加执行超时时间
                current_timeout += extend_time

                # 如果原始函数有timeout参数，也增加它
                if original_timeout > 0 :
                    kwargs[ 'timeout' ] = original_timeout + extend_time
                    # print( f"增加timeout参数至: {kwargs[ 'timeout' ]}秒" )

            print( f"{task_name} : {func.__name__} 请求失败，正在重试... (第{retry_count}次)" )
            if retry_count < max_retries :  # 如果不是最后一次重试，则等待一段时间后重试
                time.sleep( 5 * retry_count )
    print( f"请求失败次数达到上限：{max_retries}次，终止请求。重试了{retry_count}次" )
    # 这里可以添加更多的错误处理逻辑，例如记录错误信息
    if last_exception:
        raise last_exception  # 重新抛出最后一个异常
    return None


# 交互式选择菜单
def ask_select(
    options: dict,
    default_key = None,
    prompt: str = "请选择",
    timeout: int = 5,
):
    """
    显示一个数字选择菜单，接受用户输入，超时自动返回默认值。

    参数:
        options: 字典，键为选项标识（任意类型），值为显示文本
                 例如: {True: "需要填写属性", False: "不需要填写属性", "all": "不限制"}
        default_key: 超时或输入无效时的默认返回值，若为None则使用最后一个选项的键
        prompt: 提示语前缀
        timeout: 超时时间（秒），默认5秒

    返回:
        用户选择的选项键（options中的某个键），或default_key

    示例:
        >>> result = ask_select(
        ...     {True: "需要填写属性", False: "不需要填写属性", "all": "不限制"},
        ...     default_key="all",
        ...     prompt="请选择属性填写模式",
        ...     timeout=5,
        ... )
    """
    # 确保选项非空
    if not options:
        raise ValueError("options字典不能为空")

    # 设置默认值
    if default_key is None:
        default_key = list(options.keys())[-1]

    # 构建选项列表（保持字典顺序）
    items = list(options.items())

    # 显示选项
    option_lines = ", ".join([f"{i}-{label}" for i, (_, label) in enumerate(items)])
    default_label = options.get(default_key, default_key)

    # 使用线程实现跨平台超时输入
    from threading import Thread
    from queue import Queue, Empty

    result_queue = Queue()

    def input_thread():
        try:
            user_input = input().strip()
            result_queue.put(user_input)
        except EOFError:
            result_queue.put(None)

    thread = Thread(target=input_thread, daemon=True)
    thread.start()

    # 倒计时显示
    remaining = timeout
    while remaining > 0 and thread.is_alive():
        print(f"\r{prompt} ({option_lines})，{remaining} 秒后自动选择[{default_label}]: ", end="", flush=True)
        time.sleep(1)
        remaining -= 1

    # 等待线程结束（如果用户已输入）或超时
    thread.join(0)

    try:
        user_input = result_queue.get_nowait()
    except Empty:
        user_input = None

    if user_input is None:
        print(f"\n超时，自动选择[{default_label}]")
        return default_key

    # 验证输入
    try:
        choice = int(user_input)
        if 0 <= choice < len(items):
            return items[choice][0]
    except ValueError:
        pass

    # 输入无效，返回默认值
    print(f"输入无效，使用默认选项[{default_label}]")
    return default_key
