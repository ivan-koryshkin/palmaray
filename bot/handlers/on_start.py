from telegram import ForceReply, Update
from telegram.ext import ContextTypes

from users.services.users import user_create


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_user or not update.message:
        return

    user = update.effective_user
    await user_create(user.id, user.username or "")
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )
