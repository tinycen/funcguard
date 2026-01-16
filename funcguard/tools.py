import json
import base64
import hashlib
import requests
from typing import Optional, Dict, Any, Union
from .core import retry_function
from .data_models import RequestLog


def generate_md5_hash(*texts: str, encoding: str = "utf-8") -> str:
    """
    生成字符串的 MD5 哈希值，支持多个文本参数自动拼接

    :param texts: 需要生成哈希的字符串，可以传入多个参数，会自动拼接
    :param encoding: 字符串编码，默认为 utf-8
    :return: MD5 哈希值的十六进制字符串
    
    示例:
        generate_md5_hash(appid, query, salt, appkey)
        generate_md5_hash("hello", "world")  # 相当于对 "helloworld" 生成MD5
    """
    combined_text = "".join(texts)
    return hashlib.md5(combined_text.encode(encoding)).hexdigest()


# 生成 base64 格式的 Basic Auth 字符串
def encode_basic_auth(username, password):
    # 将 Username 和 Password 拼接成字符串
    auth_str = f"{username}:{password}"

    # 对字符串进行 base64 编码，并添加 'Basic ' 前缀
    auth_value = f"Basic {base64.b64encode( auth_str.encode() ).decode()}"
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
    request_log: RequestLog = RequestLog(),
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
        if request_log.save_path:
            res_log = {}
            save_fields = [
                ("save_method", "method", method),
                ("save_url", "url", url),
                ("save_headers", "headers", headers),
                ("save_body", "body", payload),
                ("save_response", "response", result),
            ]
            for attr, key, value in save_fields:
                if getattr(request_log, attr):
                    res_log[key] = value
            with open(request_log.save_path, "w", encoding="utf-8") as f:
                json.dump(res_log, f, ensure_ascii=False, indent=4)
            print(f"Request log saved to: {request_log.save_path}")

    elif return_type == "response":
        return response
    else:
        result = response.text
    return result
