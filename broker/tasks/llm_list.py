import logging

from broker import broker
from lib.database import atomic
from llms.repos.llm_repo import new_llm_repo
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown

from settings import settings


@atomic
async def _send_llm_list(session: AsyncSession, chat_id: int, topic_id: int) -> None:
    repo_llm = new_llm_repo(session)
    llms = await repo_llm.list()

    logger = logging.getLogger(__name__)
    bot = Bot(token=settings.TG_TOKEN)
    logger.info("send_llm_list: sending to chat_id=%s using token present=%s", chat_id, bool(settings.TG_TOKEN))

    if not llms:
        await bot.send_message(
            chat_id=chat_id,
            message_thread_id=topic_id,
            text=f"_{escape_markdown('No models available', version=2)}_",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return

    keyboard = [[InlineKeyboardButton(text=llm.name, callback_data=f"/llmset {llm.id}")] for llm in llms]
    markup = InlineKeyboardMarkup(keyboard)

    header = f"*{escape_markdown('Available models:', version=2)}*"
    try:
        logger.info(f"{settings.TG_TOKEN}")
        await bot.send_message(
            chat_id=chat_id, 
            text=header, 
            parse_mode=ParseMode.MARKDOWN_V2, 
            reply_markup=markup,
            message_thread_id=topic_id,
        )
    except Exception as exc:
        logger.exception("send_llm_list: failed to send message to %s: %s", chat_id, exc)


@broker.task
async def task_send_llm_list(chat_id: int, topic_id: int) -> None:
    await _send_llm_list(chat_id, topic_id)
