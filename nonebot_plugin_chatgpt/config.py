from pathlib import Path
from typing import List, Literal, Optional, Union

from nonebot import get_driver
from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    chatgpt_session_token: str = ""
    chatgpt_account: str = ""
    chatgpt_password: str = ""
    chatgpt_cd_time: int = 60
    chatgpt_proxies: Optional[str] = None
    chatgpt_refresh_interval: int = 30
    chatgpt_command: Union[str, List[str]] = ""
    chatgpt_to_me: bool = True
    chatgpt_timeout: int = 30
    chatgpt_api: str = "https://chat.openai.com/"
    chatgpt_image: bool = False
    chatgpt_image_width: int = 500
    chatgpt_priority: int = 999
    chatgpt_block: bool = True
    chatgpt_private: bool = True
    chatgpt_scope: Literal["private", "public"] = "private"
    chatgpt_data: Path = Path(__file__).parent
    chatgpt_max_rollback: int = 5
    chatgpt_detailed_error: bool = False


config = Config.parse_obj(get_driver().config)
