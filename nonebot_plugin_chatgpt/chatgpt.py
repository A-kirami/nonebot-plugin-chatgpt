import uuid
from typing import Any, Dict, Optional
from urllib.parse import urljoin

import httpx
from nonebot.log import logger
from OpenAIAuth.OpenAIAuth import OpenAIAuth
from typing_extensions import Self

try:
    import ujson as json
except ModuleNotFoundError:
    import json

SESSION_TOKEN_KEY = "__Secure-next-auth.session-token"


class Chatbot:
    def __init__(
        self,
        *,
        token: str = "",
        account: str = "",
        password: str = "",
        api: str = "https://chat.openai.com/",
        proxies: Optional[str] = None,
        timeout: int = 10,
    ) -> None:
        self.session_token = token
        self.account = account
        self.password = password
        self.api_url = api
        self.proxies = proxies
        self.timeout = timeout
        self.authorization = ""

        if self.session_token:
            self.auto_auth = False
        elif self.account and self.password:
            self.auto_auth = True
        else:
            raise ValueError("至少需要配置 session_token 或者 account 和 password")

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
            "Host": "chat.openai.com",
            "Accept": "text/event-stream",
            "Authorization": f"Bearer {self.authorization}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
            "X-Openai-Assistant-App-Id": "",
            "Connection": "close",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://chat.openai.com/chat",
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
        async with httpx.AsyncClient(proxies=self.proxies) as client:
            response = await client.post(
                urljoin(self.api_url, "backend-api/conversation"),
                headers=self.headers,
                json=self.get_payload(prompt),
                timeout=self.timeout,
            )
        if response.status_code == 429:
            return "请求过多，请放慢速度"
        if response.is_error:
            logger.opt(colors=True).error(
                f"非预期的响应内容: <r>HTTP{response.status_code}</r> {response.text}"
            )
        lines = response.text.splitlines()
        data = lines[-4][6:]
        response = json.loads(data)
        self.parent_id = response["message"]["id"]
        self.conversation_id = response["conversation_id"]
        return response["message"]["content"]["parts"][0]

    async def refresh_session(self) -> None:
        if self.auto_auth:
            self.login()
        else:
            cookies = {SESSION_TOKEN_KEY: self.session_token}
            async with httpx.AsyncClient(
                cookies=cookies,
                proxies=self.proxies,
                timeout=self.timeout,
            ) as client:
                response = await client.get(
                    urljoin(self.api_url, "api/auth/session"),
                    headers={
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.1 Safari/605.1.15",
                    },
                )
            try:
                self.session_token = (
                    response.cookies.get(SESSION_TOKEN_KEY) or self.session_token
                )
                self.authorization = response.json()["accessToken"]
            except Exception as e:
                logger.opt(colors=True, exception=e).error(
                    f"刷新会话失败: <r>HTTP{response.status_code}</r> {response.text}"
                )

    def login(self) -> None:
        auth = OpenAIAuth(self.account, self.password, bool(self.proxies), self.proxies)  # type: ignore
        try:
            auth.begin()
        except Exception as e:
            if e == "Captcha detected":
                logger.error("不支持验证码, 请使用 session token")
            raise e
        if not auth.access_token:
            logger.error("ChatGPT 登陆错误!")
        self.authorization = auth.access_token
        if auth.session_token:
            self.session_token = auth.session_token
        elif possible_tokens := auth.session.cookies.get(SESSION_TOKEN_KEY):
            if len(possible_tokens) > 1:
                self.session_token = possible_tokens[0]
            else:
                try:
                    self.session_token = possible_tokens
                except Exception as e:
                    logger.opt(exception=e).error("ChatGPT 登陆错误!")
        else:
            logger.error("ChatGPT 登陆错误!")
