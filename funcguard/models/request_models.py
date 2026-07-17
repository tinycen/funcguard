from dataclasses import dataclass


@dataclass
class RequestLog:
    save_method: bool | None = True
    save_url: bool | None = True
    save_headers: bool | None = True
    save_body: bool | None = True
    save_response: bool | None = True
    save_path: str | None = ""
