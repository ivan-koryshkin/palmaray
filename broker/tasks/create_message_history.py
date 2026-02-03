from sqlalchemy.ext.asyncio import AsyncSession
from broker.tasks.results import ChatMessage
from lib.database import atomic
from messages.services.messages import create_message_history
from broker import broker


@atomic
async def _create_message_history(session: AsyncSession, messages: list[ChatMessage]):
    for msg in messages:
        await create_message_history(
            message_id=msg["id"],
            chat_id=msg["chat_id"],
            text=msg["text"],
            user_id=msg["user_id"],
            topic_id=msg["topic_id"],
            role=msg["role"],
            image_url=msg["image_url"],
        )


@broker.task
async def task_create_message_history(messages: list[ChatMessage]):
    await _create_message_history(messages)
