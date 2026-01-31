from typing import TypedDict


class ChatMessage(TypedDict):
    id: int
    chat_id: int
    role: str
    text: str
    image_url: str
    topic_id: int
    user_id: int
