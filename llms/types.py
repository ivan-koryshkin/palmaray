from typing import TypedDict
from enum import StrEnum

class LlmResponse(TypedDict):
    text: str
    image: str


class Provider(StrEnum):
    OPENAI = "openai"