from llms.usecases.request import LlmRequest
from llms.types import LlmResponse
from settings import settings
from langchain_openai import ChatOpenAI


async def get_long_conversation_history(user_id: int, topic_id: int) -> list:
    return []

async def get_short_conversation_history(user_id: int, topic_id: int) -> list:
    return []


async def request_to_llm(user_message: str, user_id: int, topic_id: int) -> LlmResponse:
    request = LlmRequest(
        llm=ChatOpenAI(
            model="gpt-5-nano-2025-08-07",
            openai_api_key=settings.OPENAI_API_KEY
        ),
        get_long_conversation_history=get_long_conversation_history,
        get_short_conversation_history=get_short_conversation_history,
    )
    response = await request(user_message, user_id, topic_id)
    return {
        "text": response["response"]
    }
