from __future__ import annotations

from typing import TypedDict
from enum import StrEnum
from datetime import datetime

class TopicSqlFilter(TypedDict):
    chat_id: int


class MessageSqlFilter(TypedDict):
    user_id: int
    topic_id: int | None
    tokenized: bool | None
    date_from: datetime.date | None
    date_to: datetime.date | None


class TopicEmbedSqlFilter(TypedDict, total=False):
    topic_id: int
    embedding: list[float]
    top_k: int
    max_distance: float



class RoleEnum(StrEnum):
    ASSISTANT = "assistant"
    USER = "user"