from telegram import Update
from telegram.ext import ContextTypes

from lib.database import atomic
from users.services import set_user_selected_model
from llms.services import is_model_active

@atomic
async def on_callback_query(session, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # todo: refactor this
    cq = update.callback_query
    if not cq or not cq.data:
        return

    data = cq.data.strip()
    if data.startswith('/llmset'):
        parts = data.split(maxsplit=1)
        arg = parts[1] if len(parts) > 1 else ''
        await cq.answer(text=f"Selected: {arg}", show_alert=False)
        if cq.message:
            ok = await is_model_active(session, arg)
            if ok:
                await set_user_selected_model(session, update.effective_chat.id, arg)
                await cq.message.reply_text(arg)
            else:
                await cq.message.reply_text(f"Model {arg} does not found or not active anymore")
    else:
        await cq.answer()
