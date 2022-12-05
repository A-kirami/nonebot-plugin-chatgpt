from typing import Optional

from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    chatgpt_session_token: str
    chatgpt_proxies: Optional[str] = None
    chatgpt_refresh_interval: int = 30


config = Config.parse_obj(get_driver().config)
