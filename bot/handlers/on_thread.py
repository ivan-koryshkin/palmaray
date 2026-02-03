from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from users.services.users import user_create


async def on_new_thread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    await user_create(user.id, user.username or "")
    msg = await context.bot.send_message(chat_id=update.message.chat_id, text="New thread", parse_mode=ParseMode.HTML)
    msg = await context.bot.send_message(
        chat_id=update.message.chat_id, text="New thread", parse_mode=ParseMode.HTML, message_thread_id=msg.id
    )
