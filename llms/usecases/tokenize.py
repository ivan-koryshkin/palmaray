import asyncio
from typing import List

import attrs
import openai
from settings import settings

EMBEDDING_DIM = 1536


@attrs.frozen(kw_only=True, slots=True)
class TokenizeUsecase:
    model_name: str = "text-embedding-3-small"

    async def __call__(self, text: str) -> List[float]:
        openai.api_key = settings.OPENAI_API_KEY
        resp = await asyncio.to_thread(openai.Embedding.create, model=self.model_name, input=text)
        vec = resp["data"][0]["embedding"]
        if len(vec) != EMBEDDING_DIM:
            raise ValueError(f"Unexpected embedding length: {len(vec)} != {EMBEDDING_DIM}")
        return vec
