import json
import requests
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, Union
from .core import retry_function


# 发起请求
def send_request(
    method: str,
    url: str,
    headers: Dict[str, str],
    data: Optional[Any] = None,
    return_type: str = "json",
    timeout: int = 60,
    auto_retry: Optional[Dict[str, Any]] = None,
) -> Union[Dict, str, requests.Response]:
    """
    发送HTTP请求的通用函数

    :param method: HTTP方法（GET, POST等）
    :param url: 请求URL
    :param headers: 请求头
    :param data: 请求数据
    :param return_type: 返回类型（json, text, response）
    :param timeout: 请求超时时间
    :param auto_retry: 自动重试配置，格式为：
                     {"task_name": "任务名称", "max_retries": 最大重试次数, "execute_timeout": 执行超时时间}
    :return: 请求结果
    """
    if data is None:
        payload = {}
    else:
        if (isinstance(data, dict) or isinstance(data, list)) and data != {}:
            payload = json.dumps(data, ensure_ascii=False)
        else:
            payload = data
    if auto_retry is None:
        response = requests.request(
            method, url, headers=headers, data=payload, timeout=timeout
        )
    else:
        max_retries = auto_retry.get("max_retries", 5)
        execute_timeout = auto_retry.get("execute_timeout", 90)
        task_name = auto_retry.get("task_name", "")
        response = retry_function(
            requests.request,
            max_retries,
            execute_timeout,
            task_name,
            method,
            url,
            headers=headers,
            data=payload,
            timeout=timeout,
        )

    if response is None:
        raise ValueError("请求返回的响应为None")

    if return_type == "json":
        result = response.json()
    elif return_type == "response":
        return response
    else:
        result = response.text
    return result


# 打印时间
def time_log(message, i = 0, max_num = 0, s_time = None) :
    """
    打印带时间戳的日志信息，支持进度显示和预计完成时间
    
    :param message: 日志消息
    :param i: 当前进度（从0开始）
    :param max_num: 总进度数量
    :param s_time: 开始时间，用于计算预计完成时间
    :return: None
    """
    now = datetime.now( timezone( timedelta( hours = 8 ) ) )
    time_log = "{:02d}:{:02d}:{:02d}".format( now.hour, now.minute, now.second )
    if i < 2 :
        print( time_log + " " + message )
    else :
        if max_num == 0 :
            text = "{}".format( i )
        else :
            text = "{}/{}".format( i, max_num )
        # 检查是否应该显示预计完成时间和剩余时间
        if i % 10 == 0 and s_time is not None and i < max_num :
            duration = now - s_time
            ev_duration = duration / i  # 每项平均耗时
            remaining_items = max_num - i
            time_left = ev_duration * remaining_items
            end_time = now + time_left
            end_time_str = end_time.strftime( "%Y-%m-%d %H:%M" )
            remaining_time_str = str( timedelta( seconds = int( time_left.total_seconds() ) ) )
            text = text + "（{}）etr {}".format( end_time_str, remaining_time_str )
        print( time_log + " " + message + " " + text )
    return


# 计算持续时间
def time_diff(s_time = None, max_num = 0, language = "cn") :
    """
    计算并打印任务执行时间统计信息
    
    :param s_time: 开始时间
    :param max_num: 任务数量
    :param language: 语言选择（"cn"中文，其他为英文）
    :return: 如果s_time为None则返回当前时间，否则返回None
    """
    # 获取当前时间并转换为北京时间
    now = datetime.now( timezone( timedelta( hours = 8 ) ) )

    if s_time is None :
        return now

    e_time = now
    duration = e_time - s_time
    hours = duration.seconds // 3600
    duration_minutes = (duration.seconds % 3600) // 60
    seconds = duration.seconds % 60
    result = f"{hours:02d}:{duration_minutes:02d}:{seconds:02d}"

    # 将时间差转化为分钟
    minutes = round( duration.total_seconds() / 60 )
    if max_num == 0 :
        if language == "cn" :
            print( "总耗时：{}".format( result ) )
        else :
            print( "Total time: {}".format( result ) )
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

    return