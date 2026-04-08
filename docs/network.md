# 网络请求工具

FuncGuard 提供了强大的 HTTP 请求功能，支持自动重试、请求日志记录、以及 curl_cffi 兜底（用于绕过反爬虫检测）。

---

## 目录

- [send_request](#send_request) - 通用 HTTP 请求函数
- [curl_cffi_request](#curl_cffi_request) - 使用 curl_cffi 发送请求（TLS 指纹伪装）
- [check_url_valid](#check_url_valid) - 检查 URL 是否有效
- [RequestLog](#requestlog) - 请求日志配置类

---

## send_request

`send_request` 是一个通用的 HTTP 请求函数，封装了 `requests` 库，支持自动重试、请求日志记录、以及 curl_cffi 兜底功能。

### 函数签名

```python
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
    curl_fallback_impersonate: str = "chrome124",
    stream: bool = False,
) -> Union[Dict, str, requests.Response]
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `method` | `HttpMethod` | 必填 | HTTP 方法，支持 `"GET"`, `"POST"`, `"PUT"`, `"DELETE"`, `"OPTIONS"`, `"HEAD"`, `"TRACE"`, `"PATCH"` |
| `url` | `str` | 必填 | 请求 URL |
| `headers` | `Optional[Dict[str, str]]` | `None` | 请求头字典 |
| `data` | `Optional[Any]` | `None` | 请求数据。如果是 `dict` 或 `list`，会自动转为 JSON 字符串并设置 `Content-Type: application/json` |
| `return_type` | `str` | `"json"` | 返回类型，可选 `"json"`, `"text"`, `"response"` |
| `timeout` | `int` | `60` | 请求超时时间（秒） |
| `auto_retry` | `Optional[Dict[str, Any]]` | `None` | 自动重试配置，详见下方说明 |
| `request_log` | `RequestLog` | `RequestLog()` | 请求日志配置，用于保存请求和响应数据 |
| `curl_fallback` | `bool` | `False` | 是否启用 curl_cffi 兜底。当响应状态码为 403 时，自动改用 curl_cffi 重新发起请求 |
| `curl_fallback_impersonate` | `str` | `"chrome124"` | curl_cffi 使用的浏览器指纹标识，支持的值见 [curl_cffi_request](#curl_cffi_request) |
| `stream` | `bool` | `False` | 是否使用流式传输。启用后响应内容不会立即下载，可通过 `iter_content()` 分块读取，适合大文件下载场景 |

### auto_retry 配置

```python
auto_retry = {
    "task_name": "任务名称",      # 任务名称，用于日志输出
    "max_retries": 3,             # 最大重试次数
    "execute_timeout": 60         # 每次执行的超时时间（秒）
}
```

### return_type 说明

| 值 | 返回类型 | 说明 |
|----|----------|------|
| `"json"` | `Dict` | 将响应体解析为 JSON |
| `"text"` | `str` | 返回响应文本 |
| `"response"` | `requests.Response` | 返回原始 Response 对象 |

### 基础示例

#### GET 请求

```python
from funcguard import send_request

response = send_request(
    method="GET",
    url="https://api.example.com/users",
    headers={"Authorization": "Bearer token123"}
)
print(response)  # 解析后的 JSON 数据
```

#### POST 请求（自动 JSON 序列化）

```python
response = send_request(
    method="POST",
    url="https://api.example.com/users",
    headers={"Authorization": "Bearer token123"},
    data={
        "name": "张三",
        "email": "zhangsan@example.com"
    }
    # data 为 dict 时，自动转为 JSON 并设置 Content-Type
)
```

#### 获取原始 Response 对象

```python
response = send_request(
    method="GET",
    url="https://api.example.com/data",
    return_type="response"  # 返回 requests.Response 对象
)
print(response.status_code)
print(response.headers)
```

#### 流式传输请求（用于大文件下载）

```python
response = send_request(
    method="GET",
    url="https://api.example.com/largefile",
    stream=True  # 启用流式传输
)
for chunk in response.iter_content(chunk_size=8192):
    if chunk:
        # 处理数据块
        pass
```

### 自动重试示例

```python
response = send_request(
    method="POST",
    url="https://api.example.com/data",
    data={"key": "value"},
    auto_retry={
        "task_name": "数据同步任务",
        "max_retries": 5,
        "execute_timeout": 30
    }
)
```

### curl_cffi 兜底示例

当目标网站启用反爬虫（返回 403）时，自动使用 curl_cffi 重试：

```python
response = send_request(
    method="GET",
    url="https://example.com/protected",
    curl_fallback=True,  # 启用兜底
    curl_fallback_impersonate="chrome124"
)
```

结合自动重试使用：

```python
response = send_request(
    method="GET",
    url="https://example.com/protected",
    auto_retry={
        "task_name": "抓取任务",
        "max_retries": 3,
        "execute_timeout": 60
    },
    curl_fallback=True,
    curl_fallback_impersonate="safari17_0"
)
```

### 请求日志记录

```python
from funcguard import send_request, RequestLog

log_config = RequestLog(
    save_path="request_log.json",  # 日志保存路径
    save_method=True,              # 保存请求方法
    save_url=True,                 # 保存 URL
    save_headers=True,             # 保存请求头
    save_body=True,                # 保存请求体
    save_response=True             # 保存响应数据
)

response = send_request(
    method="POST",
    url="https://api.example.com/data",
    data={"key": "value"},
    request_log=log_config
)
```

---

## curl_cffi_request

`curl_cffi_request` 是使用 `curl_cffi` 库发送 HTTP 请求的内部封装，支持 TLS 指纹伪装（JA3 指纹模拟），可用于绕过基于 TLS 指纹的反爬虫检测。

### 函数签名

```python
def curl_cffi_request(
    method: HttpMethod,
    url: str,
    req_kwargs: Dict[str, Any],
    impersonate: str,
    auto_retry: Optional[Dict[str, Any]] = None,
) -> Any
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `method` | `HttpMethod` | 必填 | HTTP 方法 |
| `url` | `str` | 必填 | 请求 URL |
| `req_kwargs` | `Dict[str, Any]` | 必填 | 请求参数，包含 `headers`, `timeout`, `data` 等 |
| `impersonate` | `str` | 必填 | 浏览器指纹标识，见下方支持列表 |
| `auto_retry` | `Optional[Dict[str, Any]]` | `None` | 自动重试配置，格式同 `send_request` |

### 支持的 impersonate 值

| 值 | 说明 | User-Agent |
|----|------|------------|
| `"chrome123"` | Chrome 123 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...Chrome/123.0.0.0...` |
| `"chrome124"` | Chrome 124（默认） | `Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...Chrome/124.0.0.0...` |
| `"safari15_5"` | Safari 15.5 | `Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...Safari/605.1.15...` |
| `"safari17_0"` | Safari 17.0 | `Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)...Safari/605.1.15...` |
| `"firefox110"` | Firefox 110 | `Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0)...Firefox/110.0` |

### 使用示例

```python
from funcguard import curl_cffi_request

response = curl_cffi_request(
    method="GET",
    url="https://example.com/protected",
    req_kwargs={
        "headers": {"Accept": "text/html"},
        "timeout": 60
    },
    impersonate="chrome124"
)
print(response.text)
```

### 带自动重试的示例

```python
response = curl_cffi_request(
    method="POST",
    url="https://example.com/api",
    req_kwargs={
        "headers": {"Content-Type": "application/json"},
        "data": '{"key": "value"}',
        "timeout": 60
    },
    impersonate="safari17_0",
    auto_retry={
        "task_name": "API请求",
        "max_retries": 3,
        "execute_timeout": 90
    }
)
```

### 注意事项

1. 需要安装 `curl_cffi`：`pip install curl_cffi`
2. 如果 `impersonate` 值不在支持列表中，会抛出 `ValueError`
3. 未显式设置 `User-Agent` 时，会自动注入与 `impersonate` 匹配的 User-Agent
4. 未显式设置 `Accept` 时，会自动设置 `Accept: */*`

---

## check_url_valid

`check_url_valid` 用于快速检测 URL 是否可访问。该函数会先尝试发送 HEAD 请求，如果失败则降级到 GET 请求。

### 函数签名

```python
def check_url_valid(
    url: str,
    headers: Optional[Dict[str, str]] = None,
    max_retries: int = 3,
    curl_fallback: bool = False,
    curl_fallback_impersonate: str = "chrome124",
) -> bool
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `url` | `str` | 必填 | 要检测的 URL |
| `headers` | `Optional[Dict[str, str]]` | `None` | 请求头字典 |
| `max_retries` | `int` | `3` | 最大重试次数 |
| `curl_fallback` | `bool` | `False` | 是否启用 curl_cffi 兜底 |
| `curl_fallback_impersonate` | `str` | `"chrome124"` | curl_cffi 使用的浏览器指纹标识 |

### 返回值

- `True` - URL 可访问（返回 200 状态码）
- `False` - URL 不可访问或发生异常

### 检测逻辑

1. 首先尝试发送 HEAD 请求
2. 如果 HEAD 请求返回 200，返回 `True`
3. 如果启用了 `curl_fallback` 且 HEAD 失败，尝试使用 curl_cffi 发送 HEAD
4. 如果 HEAD 完全失败，降级到 GET 请求（使用流式传输减少内存占用）
5. GET 请求返回 200 则返回 `True`，否则返回 `False`

### 基础示例

```python
from funcguard import check_url_valid

# 简单检测
is_valid = check_url_valid("https://www.google.com")
print(is_valid)  # True 或 False

# 带自定义请求头
is_valid = check_url_valid(
    "https://api.example.com/health",
    headers={"Authorization": "Bearer token123"}
)
```

### 启用 curl_cffi 兜底

```python
# 检测可能被反爬的 URL
is_valid = check_url_valid(
    "https://example.com/protected",
    curl_fallback=True,
    curl_fallback_impersonate="chrome124",
    max_retries=3
)
```

### 批量检测示例

```python
urls = [
    "https://www.google.com",
    "https://www.github.com",
    "https://invalid-domain-12345.com"
]

for url in urls:
    is_valid = check_url_valid(url, max_retries=2)
    status = "✓ 可访问" if is_valid else "✗ 不可访问"
    print(f"{url}: {status}")
```

---

## RequestLog

`RequestLog` 是一个数据类，用于配置 `send_request` 的请求日志记录功能。

### 类定义

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class RequestLog:
    save_method: Optional[bool] = True      # 是否保存请求方法
    save_url: Optional[bool] = True         # 是否保存 URL
    save_headers: Optional[bool] = True     # 是否保存请求头
    save_body: Optional[bool] = True        # 是否保存请求体
    save_response: Optional[bool] = True    # 是否保存响应数据
    save_path: Optional[str] = ""           # 日志文件保存路径
```

### 使用示例

```python
from funcguard import send_request, RequestLog

# 完整日志记录
full_log = RequestLog(
    save_path="full_log.json",
    save_method=True,
    save_url=True,
    save_headers=True,
    save_body=True,
    save_response=True
)

# 仅记录响应数据
minimal_log = RequestLog(
    save_path="response_only.json",
    save_method=False,
    save_url=False,
    save_headers=False,
    save_body=False,
    save_response=True
)

response = send_request(
    method="POST",
    url="https://api.example.com/data",
    data={"key": "value"},
    request_log=full_log
)
```

### 日志文件格式

日志文件以 JSON 格式保存，结构如下：

```json
{
    "method": "POST",
    "url": "https://api.example.com/data",
    "headers": {"Content-Type": "application/json"},
    "body": "{\"key\": \"value\"}",
    "response": {"status": "success", "id": 123}
}
```

---

## 综合示例

### 场景：爬取需要反爬绕过的 API

```python
from funcguard import send_request, check_url_valid, RequestLog

url = "https://api.example.com/data"

# 1. 先检查 URL 是否可访问
if not check_url_valid(url, curl_fallback=True):
    print("URL 不可访问")
    exit()

# 2. 发送请求（启用反爬绕过和自动重试）
log_config = RequestLog(
    save_path="api_request.json",
    save_response=True
)

try:
    response = send_request(
        method="POST",
        url=url,
        headers={
            "Authorization": "Bearer token123",
            "X-Custom-Header": "value"
        },
        data={"page": 1, "size": 100},
        auto_retry={
            "task_name": "数据抓取",
            "max_retries": 3,
            "execute_timeout": 60
        },
        curl_fallback=True,
        curl_fallback_impersonate="chrome124",
        request_log=log_config
    )
    print(f"获取到 {len(response['data'])} 条数据")
except Exception as e:
    print(f"请求失败: {e}")
```
