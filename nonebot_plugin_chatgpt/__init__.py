from collections import defaultdict
from typing import Any, Dict, List, Type, Union

from nonebot import on_command, on_message, require
from nonebot.adapters.onebot.v11 import MessageEvent, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import _command_arg
from nonebot.rule import to_me
from nonebot.typing import T_State

from .chatgpt import Chatbot
from .config import config

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

if config.chatgpt_image:
    require("nonebot_plugin_htmlrender")

    from nonebot_plugin_htmlrender import md_to_pic

chat_bot = Chatbot(
    token=config.chatgpt_session_token,
    account=config.chatgpt_account,
    password=config.chatgpt_password,
    api=config.chatgpt_api,
    proxies=config.chatgpt_proxies,
    timeout=config.chatgpt_timeout,
)

session = defaultdict(dict)


def create_matcher(
    command: Union[str, List[str]], only_to_me: bool = True
) -> Type[Matcher]:
    params: Dict[str, Any] = {"priority": 999}

    if command:
        on_matcher = on_command
        command = [command] if isinstance(command, str) else command
        params["cmd"] = command.pop(0)
        params["aliases"] = set(command)
    else:
        on_matcher = on_message

    if only_to_me:
        params["rule"] = to_me()

    return on_matcher(**params)


matcher = create_matcher(config.chatgpt_command, config.chatgpt_to_me)


@matcher.handle()
async def ai_chat(event: MessageEvent, state: T_State) -> None:
    message = _command_arg(state) or event.get_message()
    text = message.extract_plain_text().strip()
    session_id = event.get_session_id()
    try:
        msg = await chat_bot(**session[session_id]).get_chat_response(text)
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
        logger.opt(exception=e).error(f"ChatGPT request failed: {error}")
        await matcher.finish(
            f"请求 ChatGPT 服务器时出现问题，请稍后再试\n错误信息: {error}", at_sender=True
        )
    if config.chatgpt_image:
        if msg.count("```") % 2 != 0:
            msg += "\n```"
        img = await md_to_pic(msg)
        msg = MessageSegment.image(img)
    await matcher.send(msg, at_sender=True)
    session[session_id]["conversation_id"] = chat_bot.conversation_id
    session[session_id]["parent_id"] = chat_bot.parent_id


refresh = on_command("刷新对话", aliases={"刷新会话"}, block=True, rule=to_me(), priority=1)


@refresh.handle()
async def refresh_conversation(event: MessageEvent) -> None:
    session_id = event.get_session_id()
    del session[session_id]
    await refresh.send("当前会话已刷新")


@scheduler.scheduled_job("interval", minutes=config.chatgpt_refresh_interval)
async def refresh_session() -> None:
    await chat_bot.refresh_session()
