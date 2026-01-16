from dataclasses import dataclass

from typing import Optional

@dataclass
class RequestLog:
    save_method: Optional[bool] = True
    save_url: Optional[bool] = True
    save_headers: Optional[bool] = True
    save_body: Optional[bool] = True
    save_response: Optional[bool] = True
    save_path: Optional[str] = ""
