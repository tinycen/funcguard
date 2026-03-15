"""
时间工具模块，提供时间计算、日志记录和执行时间监控功能
"""
import time
from datetime import datetime, timezone, timedelta
from .log_utils import setup_logger, _normalize_level


color_logger = setup_logger("funcguard_time_logger", message_only=True)


# 打印时间
def time_log(message, i = 0, max_num = 0, s_time = None, start_from = 0 , return_field = "progress_info", level = "") :
    """
    打印带时间戳的日志信息，支持进度显示和预计完成时间
    
    :param message: 日志消息
    :param i: 当前进度
    :param max_num: 总进度数量
    :param s_time: 开始时间，用于计算预计完成时间
    :param start_from: i是否从0开始，0表示从0开始，1表示从1开始
    :param return_field: 返回字段，支持以下：
        "progress_info" 表示完整进度信息，"remaining_time" 表示剩余时间，"end_time" 表示预计完成时间
    :param level: 日志等级，支持 DEBUG/INFO/PROGRESS/SUCCESS/WARNING/WARN/ERROR/CRITICAL/FATAL。为空时仅 print。
    :return: 根据 return_field 参数返回不同的信息
    """
    now = datetime.now( timezone( timedelta( hours = 8 ) ) )
    time_str = "{:02d}:{:02d}:{:02d}".format( now.hour, now.minute, now.second )
    progress_info = eta_time_info = etr_time_info = ""
    if i < 2 or max_num < 2 :
        if return_field in ["end_time", "remaining_time"] :
            return ""
        else:
            if level:
                color_logger.log( _normalize_level( level ), time_str + " " + message )
            else:
                print( time_str + " " + message )

    else :
        # 根据start_from参数计算实际处理的项目数
        process_item = i + 1 if start_from == 0 else i
        progress_info = "{}/{}".format( process_item, max_num )
        # 检查是否应该显示预计完成时间和剩余时间
        # 当return_field为"end_time"或"remaining_time"时，每次都计算时间
        # 否则只在每10个处理一次时计算
        should_calculate_time = (return_field in ["end_time", "remaining_time"] and process_item < max_num ) or (process_item % 10 == 0 and s_time is not None and process_item < max_num)
        
        if should_calculate_time and s_time is not None and process_item < max_num:
            duration = now - s_time
            ev_duration = duration / process_item  # 每项平均耗时
            remaining_items = max_num - process_item
            time_left = ev_duration * remaining_items
            end_time = now + time_left
            end_time_str = end_time.strftime( "%Y-%m-%d %H:%M" )
            remaining_time_str = str( timedelta( seconds = int( time_left.total_seconds() ) ) )
            eta_time_info = f"eta {end_time_str}"
            etr_time_info = f"etr {remaining_time_str}"
            progress_info = progress_info + f" ( {eta_time_info} | {etr_time_info} )"

        #  Estimated Time of Arrival（预计完成/到达时间）
        if return_field == "end_time" :
            return eta_time_info   
        
        # Estimated Time Remaining（预计剩余时间）
        elif return_field == "remaining_time" :
            return etr_time_info

        if level:
            color_logger.log( _normalize_level( level ), time_str + " " + message + " " + progress_info )
        else:
            print( time_str + " " + message + " " + progress_info )
    return progress_info


# 计算持续时间
def time_diff(s_time = None, max_num = 0, language = "cn", return_duration = 1) :
    """
    计算并打印任务执行时间统计信息
    
    :param s_time: 开始时间
    :param max_num: 任务数量
    :param language: 语言选择（"cn"中文，其他为英文）
    :param return_duration: 
        返回模式，默认为1,
        0，仅返回 total_seconds，不打印信息
        1，仅打印信息,不返回 total_seconds
        2，print 信息，并返回 total_seconds
    :return: 如果s_time为None则返回当前时间
    """
    # 获取当前时间并转换为北京时间
    now = datetime.now( timezone( timedelta( hours = 8 ) ) )

    if s_time is None :
        return now

    e_time = now
    duration = e_time - s_time
    total_seconds = int(duration.total_seconds())
    if return_duration == 0:
        return total_seconds

    hours = total_seconds // 3600
    duration_minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    result = f"{hours:02d}:{duration_minutes:02d}:{seconds:02d}"

    # 将时间差转化为分钟
    minutes = round( duration.total_seconds() / 60 )
    if max_num == 0 :
        if language == "cn" :
            print( "总耗时：{:02d} : {:02d} : {:02d}".format( hours, duration_minutes, seconds ) )
        else :
            print( "Total time: {:02d} : {:02d} : {:02d}".format( hours, duration_minutes, seconds ) )
    else :
        eve_minutes = round( minutes / max_num, 3 )
        if language == "cn" :
            print( "开始时间：{}，结束时间：{}".format( s_time.strftime( "%Y-%m-%d %H:%M" ), 
                                                     e_time.strftime( "%Y-%m-%d %H:%M" ) ) )
            print( "总耗时：{}，累计：{}分钟，数量；{}，平均耗时：{}分钟".format( result, minutes, max_num, eve_minutes ) )
        else :
            print( "Start time：{}，End time：{}".format( s_time.strftime( "%Y-%m-%d %H:%M" ), 
                                                        e_time.strftime( "%Y-%m-%d %H:%M" ) ) )
            print( "Total time: {}，Total minutes: {}，Number: {}，Average time: {} minutes".format( result, minutes, 
                                                                                                   max_num, 
                                                                                                       eve_minutes ) )
    if return_duration == 2:
        return total_seconds
    return 


# 监控程序的执行时间
def time_monitor(warning_threshold=None, print_mode=2, func=None, *args, **kwargs):
    """
    监控函数执行时间，并返回函数的执行结果和执行时间
    
    :param warning_threshold: 警告阈值（秒），如果执行耗时超过此值则打印警告
    :param print_mode: 打印模式，支持三种模式:
                      0 - 仅返回total_seconds，不打印任何信息
                      1 - 总是打印执行时间
                      2 - 仅在超时打印警告信息（默认）
    :param func: 要监控的函数
    :param args: 函数的位置参数
    :param kwargs: 函数的关键字参数
    :return: 
        print_mode == 0: 函数的执行结果, total_seconds
        print_mode == 1: 函数的执行结果
        print_mode == 2: 函数的执行结果
    """
    s_time = datetime.now( timezone( timedelta( hours = 8 ) ) )
    
    if func is None:
        raise ValueError("func is None, func must be a function")
    
    # 执行函数并获取结果
    result = func(*args, **kwargs)
    
    # 计算执行时间
    if print_mode in [ 0, 2 ]  :  # print_mode：0 和 2 需要 time_diff 内部不执行 print 但返回 total_seconds 信息
        return_duration = 0

    elif print_mode == 1 :
        return_duration = 2

    else:
        raise ValueError("print_mode must be 0, 1 or 2")

    total_seconds = time_diff(s_time, return_duration=return_duration) # pyright: ignore[reportGeneralTypeIssues]
    
    # 根据打印模式决定是否打印耗时信息
    if print_mode == 2 and warning_threshold is not None and total_seconds > warning_threshold:
        print(f"警告: 函数 {func.__name__} 执行耗时 {total_seconds:.2f}秒，超过阈值 {warning_threshold}秒")

    if print_mode == 0:
        return result, total_seconds
    
    return result


# 获取当前的时间
def get_now( from_timezone = "local", remove_tzinfo = True ):
    if from_timezone == "local" :
        now_time = datetime.now()  # 获取当前本地时间 (tz-naive) ，不包含时区信息

    elif from_timezone == "utc" :
        now_time = datetime.now( timezone.utc )  # 获取当前UTC时间 (tz-aware) ，包含时区信息

    elif from_timezone == "beijing" :   # 固定北京时间 (tz-aware) ，包含时区信息
        now_time = datetime.now( timezone( timedelta( hours = 8 ) ) )

    else :    
        raise ValueError( "Invalid timezone , must be 'local' , 'utc' , 'beijing' " )
        
    if remove_tzinfo:
        return now_time.replace( tzinfo = None )

    return now_time


# 获取时间戳
def generate_timestamp( from_timezone = "local", fmt = "millis", utc_z = False ) :
    """
    获取当前时间戳或格式化时间字符串
    
    :param from_timezone: 时区选择，决定返回的时间对象类型：
        - "local": 返回本地时间的 naive 对象（不含时区信息）。
        - "utc": 返回 UTC 时间的 aware 对象（包含 UTC 时区信息）。
        - "beijing": 返回北京时间的 aware 对象（包含 UTC+8 时区信息）。
        
        naive vs aware 的区别：
        - naive (无时区信息)：不包含时区信息的对象。它仅表示一个日期和时间，但不知道自己处于哪个时区。其含义取决于运行环境。
        - aware (有时区信息)：包含时区信息的对象。它能够准确地定位自己在绝对时间轴上的位置。
        - naive 和 aware 不能直接进行比较/计算，因为 naive 对象没有时区信息，无法确定其在时间轴上的具体位置。

    :param utc_z: 是否在 UTC 的 iso 格式后追加 Z 标志 (仅在 fmt="iso" 且时区为 UTC 时有效)
    :return: 根据 fmt 返回对应值
    """
    now_time = get_now( from_timezone, remove_tzinfo = False )

    # 格式化为ISO 8601标准格式
    if fmt == "iso" :
        if from_timezone == "utc" and utc_z :
            return now_time.strftime( '%Y-%m-%dT%H:%M:%SZ' )
        
        return now_time.strftime( '%Y-%m-%dT%H:%M:%S' )

    # 转换为毫秒级时间戳
    elif fmt == "millis" :
        return int( now_time.timestamp() * 1000 )

    elif fmt == "str" :
        return now_time.strftime( '%Y-%m-%d %H:%M:%S' )

    else :
        raise ValueError( "Invalid fmt , must be 'millis' , 'iso' or 'str'" )


# 计算日期差值
def cal_date_diff(
    old_date: datetime,
    new_date: datetime,
    unit: str = "h",
    decimal_places: int = 1,
) -> int | float:
    """
    计算两个日期的差值。

    Args:
        old_date: 原始日期
        new_date: 新日期
        unit: 返回单位，"h" 返回小时数，"day" 返回天数
        decimal_places: 保留的小数位数，默认为1

    Returns:
        int | float: 日期差值
    """
    diff = new_date - old_date
    total_seconds = diff.total_seconds()

    if unit == "h":
        return round(total_seconds / 3600, decimal_places)
    elif unit == "day":
        return round(total_seconds / 86400, decimal_places)
    else:
        raise ValueError("unit must be 'h' or 'day'")


# 时间等待
def time_wait(seconds: int = 10):
    """
    等待指定的秒数，显示倒计时
    
    :param seconds: 等待的秒数，默认值为10秒
    """
    for remaining in range(seconds, 0, -1):
        print(f"\rTime wait: {remaining}s ", end="", flush=True)
        time.sleep(1)
    # 换行
    print()
