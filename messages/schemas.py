from __future__ import annotations

from datetime import date
from enum import StrEnum
from typing import NotRequired, TypedDict


class TopicSqlFilter(TypedDict, total=False):
    id: int
    user_id: int


class MessageSqlFilter(TypedDict):
    user_id: int | None
    topic_id: int | None
    tokenized: bool | None
    date_from: date | None
    date_to: date | None
    role: NotRequired[str | None]


class TopicEmbedSqlFilter(TypedDict, total=False):
    topic_id: int
    user_id: int
    embedding: list[float]
    top_k: int
    max_distance: float


class RoleEnum(StrEnum):
    ASSISTANT = "assistant"
    USER = "user"
