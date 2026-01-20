from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from lib.database import atomic

from users.services import get_user_info


@atomic
async def on_info(session: AsyncSession, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    user_info = await get_user_info(session, user_id)

    uid = escape_markdown(str(user_info.get('id', '')), version=2)
    name = escape_markdown(user_info.get('name', '') or '—', version=2)
    selected = escape_markdown(user_info.get('selected_model') or '—', version=2)

    parts = [
        f"*User info*",
        f"*ID*: `{uid}`",
        f"*Name*: {name}",
        f"*Selected model*: `{selected}`",
    ]
    payload = "\n".join(parts)
    await update.message.reply_text(payload, parse_mode=ParseMode.MARKDOWN_V2)