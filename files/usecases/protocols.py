from typing import Protocol, runtime_checkable


@runtime_checkable
class IDownloadFile(Protocol):
    async def __call__(
        self, *, user_id: int, topic_id: int, file_id: str, file_name: str, file_size: int | None = None
    ) -> str: ...


@runtime_checkable
class IListFiles(Protocol):
    async def __call__(self, *, user_id: int, topic_id: int) -> list[tuple[str, int]]: ...


@runtime_checkable
class IReadFile(Protocol):
    async def __call__(self, *, user_id: int, topic_id: int, name: str, offset: int = 0) -> str: ...


@runtime_checkable
class IWriteFile(Protocol):
    async def __call__(self, *, user_id: int, topic_id: int, name: str, content: str) -> int: ...


@runtime_checkable
class IEditFile(Protocol):
    async def __call__(
        self, *, user_id: int, topic_id: int, name: str, old_text: str, new_text: str, replace_all: bool = False
    ) -> int: ...


@runtime_checkable
class ISendFile(Protocol):
    async def __call__(
        self, *, user_id: int, chat_id: int, topic_id: int, name: str, caption: str | None = None
    ) -> None: ...
