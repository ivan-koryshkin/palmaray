import asyncio


from llms.repos.llm_repo import new_llm_repo
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from html import escape as html_escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from lib.database import atomic


@atomic
async def on_llm_list(session: AsyncSession, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    repo_llm = new_llm_repo(session)
    llms = await repo_llm.list()
    if not llms:
        await update.message.reply_text(html_escape("No models available"), parse_mode=ParseMode.HTML)
        return

    keyboard = [
        [InlineKeyboardButton(text=llm.name, callback_data=f"/llmset {llm.id}")]
        for llm in llms
    ]
    markup = InlineKeyboardMarkup(keyboard)

    header = f"<b>{html_escape('Available models:')}</b>"
    await update.message.reply_text(header, parse_mode=ParseMode.HTML, reply_markup=markup)