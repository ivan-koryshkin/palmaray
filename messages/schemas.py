from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import TypedDict


class TopicSqlFilter(TypedDict):
    chat_id: int


class MessageSqlFilter(TypedDict):
    user_id: int
    topic_id: int | None
    tokenized: bool | None
    date_from: datetime.date | None
    date_to: datetime.date | None
    role: str | None = None


class TopicEmbedSqlFilter(TypedDict, total=False):
    topic_id: int
    embedding: list[float]
    top_k: int
    max_distance: float


class RoleEnum(StrEnum):
    ASSISTANT = "assistant"
    USER = "user"
