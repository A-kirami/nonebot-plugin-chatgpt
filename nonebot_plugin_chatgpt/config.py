from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    chatgpt_session_token: str
    chatgpt_proxies: str | None = None


config = Config.parse_obj(get_driver().config)
