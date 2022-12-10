from collections import defaultdict
from typing import Any, AsyncGenerator, Dict, List, Type, Union

from nonebot import on_command, on_message, require
from nonebot.adapters.onebot.v11 import GROUP, Message, MessageEvent, MessageSegment
from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import CommandArg, Depends, _command_arg
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

cooldown = defaultdict(int)


async def check_cooldown(
    matcher: Matcher, event: MessageEvent
) -> AsyncGenerator[None, None]:
    cooldown_time = cooldown[event.user_id] + config.chatgpt_cd_time
    if event.time < cooldown_time:
        await matcher.finish(
            f"ChatGPT 冷却中，剩余 {cooldown_time - event.time} 秒", at_sender=True
        )
    yield
    cooldown[event.user_id] = event.time


def create_matcher(
    command: Union[str, List[str]], only_to_me: bool = True, private: bool = True
) -> Type[Matcher]:
    params: Dict[str, Any] = {
        "priority": config.chatgpt_priority,
        "block": config.chatgpt_block,
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


matcher = create_matcher(
    config.chatgpt_command, config.chatgpt_to_me, config.chatgpt_private
)


@matcher.handle(parameterless=[Depends(check_cooldown)])
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
        img = await md_to_pic(msg, width=config.chatgpt_image_width)
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


export = on_command("导出对话", aliases={"导出会话"}, block=True, rule=to_me(), priority=1)


@export.handle()
async def export_conversation(event: MessageEvent) -> None:
    session_id = event.get_session_id()
    cvst = session[session_id]
    if not cvst:
        await export.finish("你还没有任何会话记录", at_sender=True)
    await export.send(
        f"已成功导出会话:\n"
        f"会话ID: {cvst['conversation_id']}\n"
        f"父消息ID: {cvst['parent_id']}",
        at_sender=True,
    )


import_ = on_command(
    "导入对话", aliases={"导入会话", "加载对话", "加载会话"}, block=True, rule=to_me(), priority=1
)


@import_.handle()
async def import_conversation(event: MessageEvent, arg: Message = CommandArg()) -> None:
    args = arg.extract_plain_text().strip().split()
    if not args:
        await import_.finish("至少需要提供会话ID", at_sender=True)
    if len(args) > 2:
        await import_.finish("提供的参数格式不正确", at_sender=True)
    session_id = event.get_session_id()
    session[session_id]["conversation_id"] = args.pop(0)
    session[session_id]["parent_id"] = args[0] if args else None
    await import_.send("已成功导入会话", at_sender=True)


@scheduler.scheduled_job("interval", minutes=config.chatgpt_refresh_interval)
async def refresh_session() -> None:
    await chat_bot.refresh_session()
