import asyncio
from langchain_openai import ChatOpenAI
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ContextTypes
from llms.usecases.request import LlmRequest
from messages.services.messages import create_message_history
from messages.types import RoleEnum
from messages.usecases.message_history import ReadShortHistory
from sqlalchemy.ext.asyncio import AsyncSession
from messages.repos.messages_repo import new_message_repo
from settings import settings
from lib.database import atomic


@atomic
async def on_message(session: AsyncSession, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async def foo(user_id, topic_id: int) -> list:
        return []
    
    message_repo=new_message_repo(session)
    request_to_llm = LlmRequest(
        llm=ChatOpenAI(
            model="gpt-5-nano-2025-08-07",
            openai_api_key=settings.OPENAI_API_KEY
        ),
        get_long_conversation_history=foo,
        get_short_conversation_history=ReadShortHistory(repo=message_repo),
    )

    await context.bot.send_chat_action(chat_id=update.message.chat_id, action=ChatAction.TYPING)
    thinking_message = await update.message.reply_text("🤔 thinking...")
    
    provider_result = await request_to_llm(
        user_id=update.message.from_user.id,
        topic_id=update.message.message_thread_id,
        user_message=update.message.text
    )

    assistant_response: str = provider_result['response']
    await thinking_message.delete()
    assistant_message = await update.message.reply_text(assistant_response, parse_mode=ParseMode.MARKDOWN)
    messages = [
        (update.message.id, RoleEnum.USER, update.message.text), 
        (assistant_message.id, RoleEnum.ASSISTANT, assistant_response)
    ]
    for msg_id, role, text in messages:
        await create_message_history(
            message_id=msg_id,
            chat_id=update.message.chat_id,
            text=text,
            user_id=update.message.from_user.id,
            topic_id=update.message.message_thread_id,
            role=role
        )
