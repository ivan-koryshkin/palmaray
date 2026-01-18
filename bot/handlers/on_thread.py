from telegram import ForceReply, Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from users.services.users import user_create

async def on_new_thread(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await user_create(user.id, user.username)
    msg = await context.bot.send_message(chat_id=update.message.chat_id, text="New thread", parse_mode=ParseMode.HTML)
    msg = await context.bot.send_message(
        chat_id=update.message.chat_id, 
        text="New thread", 
        parse_mode=ParseMode.HTML,
        message_thread_id=msg.id
    )
