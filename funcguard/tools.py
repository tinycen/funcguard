import json
import base64
import hashlib
import requests
from curl_cffi import requests as cffi_requests

from typing import Optional, Dict, Any, Union, Literal
from .core import retry_function
from .data_models import RequestLog

# HTTP 方法类型别名
HttpMethod = Literal["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "TRACE", "PATCH"]


# impersonate 名称 → 对应真实浏览器 User-Agent 映射
# 只维护 curl_cffi 支持的主流标识
_IMPERSONATE_UA_MAP: Dict[str, str] = {
    "chrome123": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "chrome124": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "safari15_5": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.5 Safari/605.1.15",
    "safari17_0": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "firefox110": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0",
}

# 默认使用的 impersonate 标识
_DEFAULT_IMPERSONATE = "chrome124"

def md5_hash(*texts: str, encoding: str = "utf-8") -> str:
    """
    生成字符串的 MD5 哈希值，支持多个文本参数自动拼接

    :param texts: 需要生成哈希的字符串，可以传入多个参数，会自动拼接
    :param encoding: 字符串编码，默认为 utf-8
    :return: MD5 哈希值的十六进制字符串

    示例:
        md5_hash(appid, query, salt, appkey)
        md5_hash("hello", "world")  # 相当于对 "helloworld" 生成MD5
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


def curl_cffi_request(
    method: HttpMethod,
    url: str,
    req_kwargs: Dict[str, Any],
    impersonate: str,
    auto_retry: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    使用 curl_cffi 发起请求的内部封装。

    :param impersonate: curl_cffi 的浏览器指纹标识
    :param auto_retry: 自动重试配置，格式同 send_request 的 auto_retry
    :raises ImportError: 如果未安装 curl_cffi
    :raises ValueError: 如果 impersonate 标识不在支持列表中
    """

    if impersonate not in _IMPERSONATE_UA_MAP:
        raise ValueError(
            f"不支持的 impersonate 值: '{impersonate}'，"
            f"可选值为: {list(_IMPERSONATE_UA_MAP.keys())}"
        )

    cffi_kwargs = dict(req_kwargs)
    cffi_kwargs["impersonate"] = impersonate

    # 注入匹配的 User-Agent（调用方未显式设置时才注入，避免覆盖业务 UA）
    headers = dict(cffi_kwargs.get("headers") or {})
    existing_keys_lower = {k.lower() for k in headers}
    if "user-agent" not in existing_keys_lower:
        headers["User-Agent"] = _IMPERSONATE_UA_MAP[impersonate]

    if "accept" not in existing_keys_lower:
        headers["Accept"] = "*/*"

    cffi_kwargs["headers"] = headers

    if auto_retry is None:
        return cffi_requests.request(method, url, **cffi_kwargs)

    max_retries = auto_retry.get("max_retries", 5)
    execute_timeout = auto_retry.get("execute_timeout", 90)
    task_name = auto_retry.get("task_name", "")
    return retry_function(
        cffi_requests.request,
        max_retries, execute_timeout, task_name,
        method, url,
        **cffi_kwargs,
    )


# 发起请求
def send_request(
    method: HttpMethod,
    url: str,
    headers: Optional[Dict[str, str]] = None,
    data: Optional[Any] = None,
    return_type: str = "json",
    timeout: int = 60,
    auto_retry: Optional[Dict[str, Any]] = None,
    request_log: RequestLog = RequestLog(),
    curl_fallback: bool = False,
    curl_fallback_impersonate: str = _DEFAULT_IMPERSONATE,
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
    :param request_log: 请求日志配置
    :param curl_fallback: 是否启用 curl_cffi 兜底。开启后，当响应状态码为 403 时，
                          自动改用 curl_cffi（含 TLS 指纹伪装）重新发起请求，默认 False。
    :param curl_fallback_impersonate: curl_cffi 使用的浏览器指纹标识，默认 "chrome124"。
                          需与对应浏览器 User-Agent 匹配（未自定义 UA 时由内部自动注入）。
                          支持的值见 _IMPERSONATE_UA_MAP。
                          若 send_request 配置了 auto_retry，curl_cffi 兜底会继承同样的重试参数。
    :return: 请求结果
    """
    payload = None

    if data is not None:
        if isinstance(data, dict) or isinstance(data, list):
            payload = json.dumps(data, ensure_ascii=False)
            if headers is None:
                headers = {"Content-Type": "application/json"}
            elif "Content-Type" not in headers:
                headers["Content-Type"] = "application/json"
        else:
            payload = data

    if headers is None:
        headers = {}

    req_kwargs = {"headers": headers, "timeout": timeout}

    # POST/PUT/PATCH 等需要 body 的方法，始终传递 data（即使为空）
    # GET/DELETE/HEAD 等无 body 方法，仅在有实际内容时传递
    if method.upper() in ("POST", "PUT", "PATCH"):
        req_kwargs["data"] = payload if payload is not None else {}
    elif payload is not None:
        req_kwargs["data"] = payload

    # ---------- 正常请求 ----------
    if auto_retry is None:
        response = requests.request(method, url, **req_kwargs)
    else:
        max_retries = auto_retry.get("max_retries", 5)
        execute_timeout = auto_retry.get("execute_timeout", 90)
        task_name = auto_retry.get("task_name", "")
        response = retry_function(
            requests.request,
            max_retries, execute_timeout, task_name,
            method, url,
            **req_kwargs,
        )

    if response is None:
        raise ValueError("请求返回的响应为None")

    # ---------- 403 → curl_cffi 兜底 ----------
    if curl_fallback and response.status_code == 403:
        response = curl_cffi_request(
            method, url, req_kwargs, curl_fallback_impersonate, auto_retry
        )

    if response is None:
        raise ValueError("curl_cffi 兜底请求返回的响应为None")

    # ---------- 结果处理 ----------
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


# 检查URL是否有效
def check_url_valid(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    max_retries: int = 3,
    curl_fallback: bool = False,
    curl_fallback_impersonate: str = _DEFAULT_IMPERSONATE,
) -> bool:
    auto_retry = {"max_retries": max_retries, "task_name": "check_url_valid"}

    try:
        response = send_request(
            method="HEAD",
            url=url,
            headers=headers,
            return_type="response",
            auto_retry=auto_retry,
            curl_fallback=curl_fallback,
            curl_fallback_impersonate=curl_fallback_impersonate,
        )
    except Exception:
        response = None

    # HEAD 成功且状态码正常，直接返回
    if response is not None and response.status_code == 200: # type: ignore
        return True

    # HEAD 失败时，如果启用了 curl_fallback，尝试使用 curl_cffi 发送 HEAD
    if curl_fallback:
        try:
            req_kwargs = {"headers": headers or {}, "timeout": 60}
            response = curl_cffi_request(
                "HEAD", url, req_kwargs, curl_fallback_impersonate, auto_retry
            )
            if response.status_code == 200: # type: ignore
                return True
        except Exception:
            pass

    # HEAD 失败（异常/405/403等）时降级到 GET
    try:
        req_kwargs = {"headers": headers or {}, "timeout": 60, "stream": True}
        response = send_request(
            method="GET",
            url=url,
            headers=headers,
            return_type="response",
            auto_retry=auto_retry,
            curl_fallback=curl_fallback,
            curl_fallback_impersonate=curl_fallback_impersonate,
        )
        return response.status_code == 200  # type: ignore
    except Exception:
        return False