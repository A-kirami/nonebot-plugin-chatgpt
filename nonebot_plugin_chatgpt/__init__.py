from nonebot import on_command, require
from nonebot.adapters.onebot.v11 import (
    GroupMessageEvent,
    Message,
    MessageEvent,
    MessageSegment,
)
from nonebot.log import logger
from nonebot.params import CommandArg, _command_arg, _command_start
from nonebot.rule import to_me
from nonebot.typing import T_State

from playwright._impl._api_types import Error as PlaywrightAPIError

from .chatgpt import Chatbot
from .config import config
from .data import setting
from .utils import Session, cooldow_checker, create_matcher

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

require("nonebot_plugin_htmlrender")

from nonebot_plugin_htmlrender import md_to_pic


chat_bot = Chatbot(
    token=setting.token or config.chatgpt_session_token,
    account=config.chatgpt_account,
    password=config.chatgpt_password,
    api=config.chatgpt_api,
    proxies=config.chatgpt_proxies,
    timeout=config.chatgpt_timeout,
)

matcher = create_matcher(
    config.chatgpt_command,
    config.chatgpt_to_me,
    config.chatgpt_private,
    config.chatgpt_priority,
    config.chatgpt_block,
)

session = Session(config.chatgpt_scope)


def check_purview(event: MessageEvent) -> bool:
    return not (
        isinstance(event, GroupMessageEvent)
        and config.chatgpt_scope == "public"
        and event.sender.role == "member"
    )


@matcher.handle(parameterless=[cooldow_checker(config.chatgpt_cd_time)])
async def ai_chat(event: MessageEvent, state: T_State) -> None:
    if not chat_bot.content:
        await chat_bot.playwright_start()
    message = _command_arg(state) or event.get_message()
    text = message.extract_plain_text().strip()
    if start := _command_start(state):
        text = text[len(start):]
    try:
        msg = await chat_bot(**session[event]).get_chat_response(text)
        if (msg == "token失效，请重新设置token") and (
            chat_bot.session_token != config.chatgpt_session_token
        ):
            await chat_bot.set_cookie(config.chatgpt_session_token)
            msg = await chat_bot(**session[event]).get_chat_response(text)
    except PlaywrightAPIError as e:
        error = f"{type(e).__name__}: {e}"
        logger.opt(exception=e).error(f"ChatGPT request failed: {error}")
        if type(e).__name__ == "TimeoutError":
            await matcher.finish(
                "ChatGPT回复已超时。", at_sender=True
            )
        elif type(e).__name__ == "Error":
            msg = "ChatGPT 目前无法回复您的问题。"
            if config.chatgpt_detailed_error:
                msg += f"\n{error}"
            else:
                msg += "可能的原因是同时提问过多，问题过于复杂等。"
            await matcher.finish(
                msg, at_sender=True
            )
    if config.chatgpt_image:
        if msg.count("```") % 2 != 0:
            msg += "\n```"
        img = await md_to_pic(msg, width=config.chatgpt_image_width)
        msg = MessageSegment.image(img)
    await matcher.send(msg, at_sender=True)
    session[event] = chat_bot.conversation_id, chat_bot.parent_id


refresh = on_command("刷新对话", aliases={"刷新会话"}, block=True, rule=to_me(), priority=1)


@refresh.handle()
async def refresh_conversation(event: MessageEvent) -> None:
    if not check_purview(event):
        await import_.finish("当前为公共会话模式, 仅支持群管理操作")
    del session[event]
    await refresh.send("当前会话已刷新")


export = on_command("导出对话", aliases={"导出会话"}, block=True, rule=to_me(), priority=1)


@export.handle()
async def export_conversation(event: MessageEvent) -> None:
    if cvst := session[event]:
        await export.send(
            f"已成功导出会话:\n"
            f"会话ID: {cvst['conversation_id'][-1]}\n"
            f"父消息ID: {cvst['parent_id'][-1]}",
            at_sender=True,
        )
    else:
        await export.finish("你还没有任何会话记录", at_sender=True)


import_ = on_command(
    "导入对话", aliases={"导入会话", "加载对话", "加载会话"}, block=True, rule=to_me(), priority=1
)


@import_.handle()
async def import_conversation(event: MessageEvent, arg: Message = CommandArg()) -> None:
    if not check_purview(event):
        await import_.finish("当前为公共会话模式, 仅支持群管理操作")
    args = arg.extract_plain_text().strip().split()
    if not args:
        await import_.finish("至少需要提供会话ID", at_sender=True)
    if len(args) > 2:
        await import_.finish("提供的参数格式不正确", at_sender=True)
    session[event] = args.pop(0), args[0] if args else None
    await import_.send("已成功导入会话", at_sender=True)


save = on_command("保存对话", aliases={"保存会话"}, block=True, rule=to_me(), priority=1)


@save.handle()
async def save_conversation(event: MessageEvent, arg: Message = CommandArg()) -> None:
    if not check_purview(event):
        await save.finish("当前为公共会话模式, 仅支持群管理操作")
    if session[event]:
        name = arg.extract_plain_text().strip()
        session.save(name, event)
        await save.send(f"已将当前会话保存为: {name}", at_sender=True)
    else:
        await save.finish("你还没有任何会话记录", at_sender=True)


check = on_command("查看对话", aliases={"查看会话"}, block=True, rule=to_me(), priority=1)


@check.handle()
async def check_conversation(event: MessageEvent) -> None:
    name_list = "\n".join(list(session.find(event).keys()))
    await check.send(f"已保存的会话有:\n{name_list}", at_sender=True)


switch = on_command("切换对话", aliases={"切换会话"}, block=True, rule=to_me(), priority=1)


@switch.handle()
async def switch_conversation(event: MessageEvent, arg: Message = CommandArg()) -> None:
    if not check_purview(event):
        await switch.finish("当前为公共会话模式, 仅支持群管理操作")
    name = arg.extract_plain_text().strip()
    try:
        session[event] = session.find(event)[name]
        await switch.send(f"已切换到会话: {name}", at_sender=True)
    except KeyError:
        await switch.send(f"找不到会话: {name}", at_sender=True)


@scheduler.scheduled_job("interval", minutes=config.chatgpt_refresh_interval)
async def refresh_session() -> None:
    await chat_bot.refresh_session()
    setting.token = chat_bot.session_token
    setting.save()


rollback = on_command("回滚对话", aliases={"回滚会话"}, block=True, rule=to_me(), priority=1)


@rollback.handle()
async def rollback_conversation(event: MessageEvent, arg: Message = CommandArg()):
    num = arg.extract_plain_text().strip()
    if num.isdigit():
        num = int(num)
        if session[event]:
            count = session.count(event)
            if num > count:
                await rollback.finish(f"历史会话数不足，当前历史会话数为{count}", at_sender=True)
            else:
                for _ in range(num):
                    session.pop(event)
                await rollback.send(f"已成功回滚{num}条会话", at_sender=True)
        else:
            await save.finish("你还没有任何会话记录", at_sender=True)
    else:
        await rollback.finish(
            f"请输入有效的数字，最大回滚数为{config.chatgpt_max_rollback}", at_sender=True
        )
