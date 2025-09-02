import json
import requests
from . import core
# 使用 from .core import retry_function 会导致测试失败

# 发起请求
def send_request( method , url , headers , data = None , return_type = "json" , timeout = 60 , auto_retry = None ) :
    '''
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
    '''
    if data is None :
        payload = { }
    else :
        if (isinstance( data , dict ) or isinstance( data , list )) and data != { } :
            payload = json.dumps( data , ensure_ascii = False )
        else :
            payload = data
    if auto_retry is None :
        response = requests.request( method , url , headers = headers , data = payload , timeout = timeout )
    else :
        max_retries = auto_retry.get( "max_retries" , 5 )
        execute_timeout = auto_retry.get( "execute_timeout" , 90 )
        task_name = auto_retry.get( "task_name" , "" )
        response = core.retry_function( requests.request , max_retries , execute_timeout , task_name , method , url ,
                                        headers = headers , data = payload , timeout = timeout )

    if response is None:
        raise ValueError("请求返回的响应为None")
    
    if return_type == "json" :
        result = response.json()
    elif return_type == "response" :
        return response
    else :
        result = response.text
    return result