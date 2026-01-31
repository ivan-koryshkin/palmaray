import logging

from aiogram import Bot
from langchain_openai import ChatOpenAI
from broker import broker
from lib.database import atomic
from sqlalchemy.ext.asyncio import AsyncSession

from lib.services import summarize_text, tokenize
from sqlalchemy.ext.asyncio import AsyncSession
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown

from llms.usecases.request import LlmRequest
from messages.repos.messages_repo import new_message_repo
from messages.repos.topic_embed_repo import new_topic_embed_repo
from messages.schemas import RoleEnum
from messages.services.messages import create_message_history
from messages.usecases.archive_messages import ArchiveMessages
from messages.usecases.message_history import ReadContextHistory, ReadShortHistory
from settings import settings
from users.services.users import get_user_info



@atomic
async def _response_to_user(
    session: AsyncSession,
    user_id: int,
    chat_id: int,
    topic_id: int,
    user_message_text: str,
    user_message_id: str,
    image_url: str | None = None
) -> None:
    logger = logging.getLogger(__name__)
    bot = Bot(token=settings.TG_TOKEN)
    logger.info("response_to_user: sending to chat_id=%s token present=%s", chat_id, bool(settings.TG_TOKEN))
    try:
        thinking_message = await bot.send_message(
            chat_id=chat_id,
            message_thread_id=topic_id,
            text=f"Thinking",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
    except Exception as exc:
        logger.exception("response_to_user: failed to send thinking message to %s: %s", chat_id, exc)
        return
    message_repo = new_message_repo(session)
    topic_emb_repo = new_topic_embed_repo(session)
    user_info = await get_user_info(session, user_id)

    request_to_llm = LlmRequest(
        llm=ChatOpenAI(model=user_info["selected_model"], openai_api_key=settings.OPENAI_API_KEY),
        get_long_conversation_history=ReadContextHistory(repo=topic_emb_repo, tokenize=tokenize),
        get_short_conversation_history=ReadShortHistory(repo=message_repo),
        archive_conversation_history=ArchiveMessages(
            repo_msg=message_repo, repo_topic_embed=topic_emb_repo, tokenize=tokenize, summarize=summarize_text
        ),
    )

    provider_result = await request_to_llm(
        user_id=user_id,
        topic_id=topic_id,
        user_message=user_message_text,
        image_url=image_url,
    )

    assistant_response: str = provider_result.get("response", "")
    safe_for_send = escape_markdown(assistant_response, version=1)
    await thinking_message.edit_text(safe_for_send, parse_mode=ParseMode.MARKDOWN)

    messages = [
        (user_message_id, RoleEnum.USER, user_message_text, image_url),
        (thinking_message.id, RoleEnum.ASSISTANT, assistant_response, None),
    ]
    for msg_id, role, text, img_url in messages:
        await create_message_history(
            message_id=msg_id,
            chat_id=user_message_id,
            text=text,
            user_id=user_id,
            topic_id=topic_id,
            role=role,
            image_url=img_url,
        )


@broker.task
async def response_to_user(
    user_id: int,
    chat_id: int,
    topic_id: int,
    user_message_text: str,
    user_message_id: str,
    image_url: str | None = None
) -> None:
    await _response_to_user(user_id, chat_id, topic_id, user_message_text, user_message_id, image_url)
