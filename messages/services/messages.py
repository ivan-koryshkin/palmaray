from datetime import datetime, timedelta

from messages.models import MessageModel
from messages.repos.messages_repo import new_message_repo
from messages.repos.topics_repo import new_topic_repo
from messages.schemas import MessageSqlFilter, RoleEnum
from messages.usecases.message_delete import DeleteOldMessage
from messages.usecases.message_history import CreateMessageHistory
from messages.usecases.message_save import SaveMessage
from messages.usecases.topic_save import SaveTopic
from sqlalchemy.ext.asyncio import AsyncSession

from lib.database import atomic


@atomic
async def create_message_history(
    session: AsyncSession,
    message_id: int,
    chat_id: int,
    text: str,
    user_id: int,
    topic_id: int | None = None,
    role: RoleEnum = RoleEnum.USER,
    image_url: str | None = None,
) -> int | None:
    message_repo = new_message_repo(session)
    topic_repo = new_topic_repo(session)
    create_history = CreateMessageHistory(
        save_message=SaveMessage(repo=message_repo, encrypt_message=lambda x: x),
        save_topic=SaveTopic(repo=topic_repo),
        delete_old_messages=DeleteOldMessage(repo=message_repo),
    )
    return await create_history(message_id, chat_id, text, user_id, topic_id, role=role, image_url=image_url)


@atomic
async def get_old_messages(session: AsyncSession) -> list[MessageModel]:
    message_repo = new_message_repo(session)
    date_from = (datetime.now() - timedelta(days=3)).date()
    return await message_repo.list(
        flt=MessageSqlFilter(
            user_id=0, topic_id=None, tokenized=None, date_from=date_from, date_to=datetime.now().date(), role=None
        )
    )
