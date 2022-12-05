import uuid
from typing import Any, Dict, Optional

import httpx
from nonebot.exception import NetworkError
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
        }

    def reset_chat(self) -> None:
        self.conversation_id = None
        self.parent_id = self.id

    def generate_data(self, prompt: str) -> Dict[str, Any]:
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
                "https://chat.openai.com/backend-api/conversation",
                headers=self.headers,
                data=json.dumps(self.generate_data(prompt)),  # type: ignore
                timeout=config.chatgpt_timeout,
            )
        try:
            response = response.text.splitlines()[-4]
            response = response[6:]
        except Exception as e:
            raise NetworkError(f"Abnormal response content: {response.text}") from e
        response = json.loads(response)
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
            response = await client.get("https://chat.openai.com/api/auth/session")
        try:
            self.session_token = response.cookies.get(SESSION_TOKEN, "")  # type: ignore
            self.authorization = response.json()["accessToken"]
        except Exception as e:
            raise RuntimeError("Error refreshing session") from e
