import asyncio
from typing import Any, Awaitable, Callable

import attrs
from langchain_core.messages import BaseMessage
from messages.models import MessageModel, TopicEmbedModel
from messages.schemas import MessageSqlFilter, RoleEnum, TopicEmbedSqlFilter
from messages.usecases.protocols import IDeleteMessages, IMessageSave, ITopicSave

from lib.repo import GenericRepo


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
        role: RoleEnum = RoleEnum.USER,
        image_url: str | None = None,
    ) -> int:
        assert topic_id
        topic_id = await self.save_topic(
            id=topic_id,
            name=f"default topic {topic_id}",
            user_id=user_id,
        )

        save_task = self.save_message(
            message_id=message_id,
            chat_id=chat_id,
            text=text,
            topic_id=topic_id,
            role=role,
            image_url=image_url,
        )
        delete_task = self.delete_old_messages(topic_id, 15)

        saved, _ = await asyncio.gather(save_task, delete_task)
        return topic_id


@attrs.frozen(kw_only=True, slots=True)
class ReadShortHistory:
    repo: GenericRepo[MessageModel, MessageSqlFilter]

    async def __call__(self, user_id: int, topic_id: int) -> list[BaseMessage]:
        messages = await self.repo.list(
            flt=MessageSqlFilter(
                user_id=user_id, topic_id=topic_id, tokenized=None, date_from=None, date_to=None, role=None
            )
        )

        result: list[BaseMessage] = []
        for msg in messages:
            msg_dict = msg.to_dict()
            role = msg_dict.get("role", "")
            message_text = msg_dict.get("message", "")

            if role == "user":
                from langchain_core.messages import HumanMessage

                result.append(HumanMessage(content=message_text))
            elif role == "assistant":
                from langchain_core.messages import AIMessage

                result.append(AIMessage(content=message_text))

        return result


@attrs.frozen(kw_only=True, slots=True)
class ReadContextHistory:
    repo: GenericRepo[TopicEmbedModel, TopicEmbedSqlFilter]
    tokenize: Callable[[str], Awaitable[list[float]]]

    async def __call__(self, user_id: int, user_message: str) -> list[dict[str, Any]]:
        vector = await self.tokenize(user_message)
        context_chunks = await self.repo.list(flt={"embedding": vector}, limit=3)
        return [{"chunk": c.chunk, "image_url": c.image_url} for c in context_chunks]
