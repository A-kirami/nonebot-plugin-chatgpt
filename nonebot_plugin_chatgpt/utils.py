from collections import defaultdict
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple, Type, Union

from nonebot import on_command, on_message
from nonebot.adapters.onebot.v11 import GROUP, MessageEvent
from nonebot.matcher import Matcher
from nonebot.params import Depends
from nonebot.rule import to_me


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
    def __init__(self) -> None:
        super().__init__()

    def __getitem__(self, event: MessageEvent) -> Dict[str, Any]:
        return super().__getitem__(self.id(event))

    def __setitem__(
        self, event: MessageEvent, value: Tuple[Optional[str], Optional[str]]
    ) -> None:
        super().__setitem__(
            self.id(event),
            {
                "conversation_id": value[0],
                "parent_id": value[1],
            },
        )

    def __delitem__(self, event: MessageEvent) -> None:
        return super().__delitem__(self.id(event))

    def __missing__(self, _) -> Dict[str, Any]:
        return {}

    def id(self, event: MessageEvent) -> str:
        return event.get_session_id()
