from typing import Protocol, Callable

from lib.repo import GenericRepo
from messages.models import MessageModel, TopicModel
from messages.types import MessageSqlFilter, RoleEnum, TopicSqlFilter


class ITopicSave(Protocol):
    repo: GenericRepo[TopicModel, TopicSqlFilter]

    async def __call__(self, id: int, name: str, user_id: int) -> int: ...


class IMessageSave(Protocol):
    repo: GenericRepo[MessageModel, MessageSqlFilter]
    encrypt_message: Callable[[str], str]

    async def __call__(
        self, *, message_id: int, chat_id: int, text: str, topic_id: int, role: RoleEnum
    ) -> int | None: ...

class IDeleteMessages:
    max_count: int
    repo: GenericRepo[MessageModel, MessageSqlFilter]
    
    async def __call__(self, topic_id: int, count: int) -> bool: ...


class ITokenizeMessages(Protocol):
    async def __call__(self, message_ids: list[int]) -> bool: ...



class IReadShortHistory:
    repo: GenericRepo[MessageModel, MessageSqlFilter]

    async def __call__(self, user_id: int, topic_id: int) -> list[MessageModel]: ...


class ITokenize(Protocol):
    async def __call__(self, text: str) -> str: ...

class ISummarize(Protocol):
    async def __call__(self, text: str) -> str: ...