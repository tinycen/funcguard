class FuncguardTimeoutError(Exception):
    pass

import time
from concurrent.futures import ThreadPoolExecutor , TimeoutError

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

        except BaseException as e :
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
