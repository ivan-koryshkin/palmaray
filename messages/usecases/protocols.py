from typing import Protocol, runtime_checkable

from messages.models import MessageModel
from messages.schemas import RoleEnum


@runtime_checkable
class ITopicSave(Protocol):
    async def __call__(self, id: int, name: str, user_id: int) -> int: ...


@runtime_checkable
class IMessageSave(Protocol):
    async def __call__(
        self, *, message_id: int, chat_id: int, text: str, topic_id: int, role: RoleEnum, image_url: str | None = None
    ) -> int | None: ...


@runtime_checkable
class IDeleteMessages(Protocol):
    async def __call__(self, topic_id: int, count: int) -> bool: ...


@runtime_checkable
class ITokenizeMessages(Protocol):
    async def __call__(self, message_ids: list[int]) -> bool: ...


@runtime_checkable
class IReadShortHistory(Protocol):
    async def __call__(self, user_id: int, topic_id: int) -> list[MessageModel]: ...


@runtime_checkable
class ITokenize(Protocol):
    async def __call__(self, text: str) -> list[float]: ...


@runtime_checkable
class ISummarize(Protocol):
    async def __call__(self, text: str) -> str: ...
