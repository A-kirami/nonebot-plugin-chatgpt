from typing import List, Optional, Union

from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    chatgpt_session_token: str
    chatgpt_proxies: Optional[str] = None
    chatgpt_refresh_interval: int = 30
    chatgpt_command: Union[str, List[str]] = ""
    chatgpt_to_me: bool = True
    chatgpt_timeout: int = 10


config = Config.parse_obj(get_driver().config)
