from telegram import Update
from telegram.ext import ContextTypes

from broker.tasks.llm_list import send_llm_list


async def on_llm_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await send_llm_list.kiq(update.effective_chat.id, update.message.message_thread_id)
