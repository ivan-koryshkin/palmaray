import attrs

from lib.repo import GenericRepo
from messages.models import MessageModel
from messages.types import MessageSqlFilter, RoleEnum
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from .protocols import IDeleteMessages, IMessageSave, ITopicSave


@attrs.frozen(kw_only=True, slots=True)
class CreateMessageHistory:
    save_message: IMessageSave
    save_topic: ITopicSave
    delete_old_messages: IDeleteMessages

    async def __call__(
        self,
        message_id: int,
        chat_id: int,
        text: str,
        user_id: int,
        topic_id: int | None = None,
        role: RoleEnum = RoleEnum.USER
    ) -> int:
        topic_id = await self.save_topic(
            id=topic_id,
            name=f"default topic {topic_id}",
            user_id=user_id,
        )
        msg = await self.save_message(
            message_id=message_id,
            chat_id=chat_id,
            text=text,
            topic_id=topic_id,
            role=role
        )
        await self.delete_old_messages(topic_id, 15)
        return msg


@attrs.frozen(kw_only=True, slots=True)
class ReadShortHistory:
    repo: GenericRepo[MessageModel, MessageSqlFilter]

    async def __call__(self, user_id: int, topic_id: int) -> list[BaseMessage]:
        messages = await self.repo.list(flt={
            "user_id": user_id,
            "topic_id": topic_id
        })
        result: list[BaseMessage] = []
        for message in messages:
            if message.role == RoleEnum.ASSISTANT.value:
                msg = AIMessage(content=message.text)
            else:
                msg = HumanMessage(content=message.text)
            result.append(msg)
        return result