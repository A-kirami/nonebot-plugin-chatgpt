from collections import defaultdict

from nonebot import on_message, require
from nonebot.adapters.onebot.v11 import MessageEvent
from nonebot.rule import to_me

from .chatgpt import Chatbot
from .config import config

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler

chat = on_message(rule=to_me(), priority=999)

chat_bot = Chatbot()

session = defaultdict(dict)


@chat.handle()
async def _(event: MessageEvent) -> None:
    text = event.get_plaintext()
    session_id = event.get_session_id()
    msg = await chat_bot(**session[session_id]).get_chat_response(text)
    await chat.send(msg, at_sender=True)
    session[session_id]["conversation_id"] = chat_bot.conversation_id
    session[session_id]["parent_id"] = chat_bot.parent_id


@scheduler.scheduled_job("interval", minutes=config.chatgpt_refresh_interval)
async def refresh_session() -> None:
    await chat_bot.refresh_session()
