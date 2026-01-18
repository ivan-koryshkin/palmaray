from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from settings import settings


async def get_text_embedding(text: str) -> list[float]:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
        encoding_format="float"
    )
    return response.data[0].embedding


async def summarize_text(text: str) -> str:
    prompt = f"""
    Extract core meaning from this text. 
    Remove filler words, keep only essential factual content. 
    Respond in the same language as input:\n\n{text}"
    """
    client = ChatOpenAI(
        model="gpt-5-mini", 
        openai_api_key=settings.OPENAI_API_KEY
    )
    
    message = HumanMessage(content=prompt)
    response = client.invoke([message])
    return response.content
