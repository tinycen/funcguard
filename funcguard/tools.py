import json
import base64
import requests
from typing import Optional, Dict, Any, Union
from .core import retry_function

# 生成 base64 格式的 Basic Auth 字符串


def encode_basic_auth(username, password):
    # 将 Username 和 Password 拼接成字符串
    auth_str = f'{username}:{password}'

    # 对字符串进行 base64 编码，并添加 'Basic ' 前缀
    auth_value = f'Basic {base64.b64encode( auth_str.encode() ).decode()}'
    return auth_value


# 发起请求
def send_request(
    method: str,
    url: str,
    headers: Optional[Dict[str, str]] = None,
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
        if data and isinstance(data, dict):
            payload = json.dumps(data, ensure_ascii=False)
            if headers is None:
                headers = {"Content-Type": "application/json"}
            elif "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"
        elif data and isinstance(data, list):
            payload = json.dumps(data, ensure_ascii=False)
        else:
            payload = data

    if headers is None:
        headers = {}

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
