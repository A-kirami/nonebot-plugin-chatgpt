import uuid
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from nonebot.log import logger
from typing_extensions import Self

from .config import config

try:
    import ujson as json
except ModuleNotFoundError:
    import json

SESSION_TOKEN = "__Secure-next-auth.session-token"


class Chatbot:
    def __init__(self) -> None:
        self.session_token = config.chatgpt_session_token
        self.authorization = None

    def __call__(
        self, conversation_id: Optional[str] = None, parent_id: Optional[str] = None
    ) -> Self:
        self.conversation_id = conversation_id
        self.parent_id = parent_id or self.id
        return self

    @property
    def id(self) -> str:
        return str(uuid.uuid4())

    @property
    def headers(self) -> Dict[str, str]:
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.authorization}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
        }

    def get_payload(self, prompt: str) -> Dict[str, Any]:
        return {
            "action": "next",
            "messages": [
                {
                    "id": self.id,
                    "role": "user",
                    "content": {"content_type": "text", "parts": [prompt]},
                }
            ],
            "conversation_id": self.conversation_id,
            "parent_message_id": self.parent_id,
            "model": "text-davinci-002-render",
        }

    async def get_chat_response(self, prompt: str) -> str:
        if not self.authorization:
            await self.refresh_session()
        async with httpx.AsyncClient(proxies=config.chatgpt_proxies) as client:  # type: ignore
            response = await client.post(
                urljoin(config.chatgpt_api, "backend-api/conversation"),
                headers=self.headers,
                json=self.get_payload(prompt),
                timeout=config.chatgpt_timeout,
            )
        if response.status_code == 429:
            return "请求过多，请放慢速度"
        if response.is_error:
            logger.opt(colors=True).error(
                f"Unexpected response content: <r>HTTP{response.status_code}</r> {response.text}"
            )
        lines = response.text.splitlines()
        data = lines[-4][6:]
        response = json.loads(data)
        self.parent_id = response["message"]["id"]
        self.conversation_id = response["conversation_id"]
        return response["message"]["content"]["parts"][0]

    async def refresh_session(self) -> None:
        cookies = {SESSION_TOKEN: self.session_token}
        async with httpx.AsyncClient(
            cookies=cookies,
            proxies=config.chatgpt_proxies,  # type: ignore
            timeout=config.chatgpt_timeout,
        ) as client:
            response = await client.get(
                urljoin(config.chatgpt_api, "api/auth/session"),
                headers={
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
                },
            )
        try:
            self.session_token = response.cookies.get(SESSION_TOKEN, "")  # type: ignore
            self.authorization = response.json()["accessToken"]
        except Exception as e:
            logger.opt(colors=True, exception=e).error(
                f"Refresh session failed: <r>HTTP{response.status_code}</r> {response.text}"
            )
