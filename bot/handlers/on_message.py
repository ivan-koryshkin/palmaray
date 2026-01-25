import asyncio

from langchain_openai import ChatOpenAI
from llms.usecases.request import LlmRequest
from messages.repos.messages_repo import new_message_repo
from messages.repos.topic_embed_repo import new_topic_embed_repo
from messages.services.messages import create_message_history
from messages.schemas import RoleEnum
from messages.usecases.archive_messages import ArchiveMessages
from messages.usecases.message_history import ReadShortHistory, ReadContextHistory
from settings import settings
from sqlalchemy.ext.asyncio import AsyncSession
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from lib.database import atomic
from lib.services import summarize_text, tokenize
from users.services import get_user_info


async def _get_image_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str | None:
    if not update.message.photo:
        return None

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        return file.file_path
    except Exception as e:
        print(f"Error getting image: {e}")


@atomic
async def on_message(session: AsyncSession, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message_repo = new_message_repo(session)
    topic_emb_repo = new_topic_embed_repo(session)
    user_info = await get_user_info(session, update.message.from_user.id)

    request_to_llm = LlmRequest(
        llm=ChatOpenAI(model=user_info["selected_model"], openai_api_key=settings.OPENAI_API_KEY),
        get_long_conversation_history=ReadContextHistory(repo=topic_emb_repo, tokenize=tokenize),
        get_short_conversation_history=ReadShortHistory(repo=message_repo),
        archive_conversation_history=ArchiveMessages(
            repo_msg=message_repo, repo_topic_embed=topic_emb_repo, tokenize=tokenize, summarize=summarize_text
        ),
    )

    image_url = await _get_image_url(update, context)

    if not update.message.text and not image_url:
        return

    user_message = update.message.text or ""

    stop_event = asyncio.Event()
    thinking_message = await update.message.reply_text("🤔 thinking")

    async def animate_thinking(msg, ev: asyncio.Event):
        frames = ["Thinking", "Thinking 🤔", "Thinking 🤔🤔", "Thinking 🤔🤔🤔"]
        i = 0
        try:
            while not ev.is_set():
                text = frames[i % len(frames)]
                try:
                    await msg.edit_text(text)
                except Exception:
                    pass
                i += 1
                await asyncio.sleep(1.2)
        except asyncio.CancelledError:
            return

    anim_task = asyncio.create_task(animate_thinking(thinking_message, stop_event))

    provider_result = await request_to_llm(
        user_id=update.message.from_user.id,
        topic_id=update.message.message_thread_id,
        user_message=user_message,
        image_url=image_url,
    )

    assistant_response: str = provider_result.get("response", "")
    stop_event.set()
    if not anim_task.done():
        await anim_task
    safe_for_send = escape_markdown(assistant_response, version=1)
    try:
        assistant_message = await thinking_message.edit_text(safe_for_send, parse_mode=ParseMode.MARKDOWN)
    except Exception:
        assistant_message = await update.message.reply_text(safe_for_send, parse_mode=ParseMode.MARKDOWN)
    messages = [
        (update.message.id, RoleEnum.USER, user_message, image_url),
        (assistant_message.id, RoleEnum.ASSISTANT, assistant_response, None),
    ]
    for msg_id, role, text, img_url in messages:
        await create_message_history(
            message_id=msg_id,
            chat_id=update.message.chat_id,
            text=text,
            user_id=update.message.from_user.id,
            topic_id=update.message.message_thread_id,
            role=role,
            image_url=img_url,
        )
