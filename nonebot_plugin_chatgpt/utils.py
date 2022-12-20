from collections import defaultdict, deque
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    List,
    Literal,
    Optional,
    Tuple,
    Type,
    Union,
)

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.rule import to_me

from .config import config
from .data import setting


def cooldow_checker(cd_time: int) -> Any:
    cooldown = defaultdict(int)

    async def check_cooldown(
        matcher: Matcher, event: MessageEvent
    ) -> AsyncGenerator[None, None]:
        cooldown_time = cooldown[event.user_id] + cd_time
        if event.time < cooldown_time:
            await matcher.finish(
                f"ChatGPT 冷却中，剩余 {cooldown_time - event.time} 秒", at_sender=True
            )
        yield
        cooldown[event.user_id] = event.time

    return Depends(check_cooldown)


def create_matcher(
    command: Union[str, List[str]],
    only_to_me: bool = True,
    private: bool = True,
    priority: int = 999,
    block: bool = True,
) -> Type[Matcher]:
    params: Dict[str, Any] = {
        "priority": priority,
        "block": block,
    }

    if command:
        on_matcher = on_command
        command = [command] if isinstance(command, str) else command
        params["cmd"] = command.pop(0)
        params["aliases"] = set(command)
    else:
        on_matcher = on_message

    if only_to_me:
        params["rule"] = to_me()
    if not private:
        params["permission"] = GROUP

    return on_matcher(**params)


class Session(dict):
    def __init__(self, scope: Literal["private", "public"]) -> None:
        super().__init__()
        self.is_private = scope == "private"

    def __getitem__(self, event: MessageEvent) -> Dict[str, Any]:
        return super().__getitem__(self.id(event))

    def __setitem__(
        self,
        event: MessageEvent,
        value: Union[Tuple[Optional[str], Optional[str]], Dict[str, Any]],
    ) -> None:
        if isinstance(value, tuple):
            conversation_id, parent_id = value
        else:
            conversation_id = value["conversation_id"]
            parent_id = value["parent_id"]
        if self[event]:
            if isinstance(value, tuple):
                self[event]["conversation_id"].append(conversation_id)
                self[event]["parent_id"].append(parent_id)
        else:
            super().__setitem__(
                self.id(event),
                {
                    "conversation_id": deque(
                        [conversation_id], maxlen=config.chatgpt_max_rollback
                    ),
                    "parent_id": deque([parent_id], maxlen=config.chatgpt_max_rollback),
                },
            )

    def __delitem__(self, event: MessageEvent) -> None:
        sid = self.id(event)
        if sid in self:
            super().__delitem__(sid)

    def __missing__(self, _) -> Dict[str, Any]:
        return {}

    def id(self, event: MessageEvent) -> str:
        if self.is_private:
            return event.get_session_id()
        return str(
            event.group_id if isinstance(event, GroupMessageEvent) else event.user_id
        )

    def save(self, name: str, event: MessageEvent) -> None:
        sid = self.id(event)
        if setting.session.get(sid) is None:
            setting.session[sid] = {}
        setting.session[sid][name] = {
            "conversation_id": self[event]["conversation_id"][-1],
            "parent_id": self[event]["parent_id"][-1],
        }
        setting.save()

    def find(self, event: MessageEvent) -> Dict[str, Any]:
        sid = self.id(event)
        return setting.session[sid]

    def count(self, event: MessageEvent) -> int:
        return len(self[event]["conversation_id"])

    def pop(self, event: MessageEvent) -> Tuple[str, str]:
        conversation_id = self[event]["conversation_id"].pop()
        parent_id = self[event]["parent_id"].pop()
        return conversation_id, parent_id
