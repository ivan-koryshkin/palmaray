from sqlalchemy.ext.asyncio import AsyncSession
from llms.repos.llm_repo import new_llm_repo


async def is_model_active(session: AsyncSession, model_id: str) -> bool:
    repo = new_llm_repo(session)
    model = await repo.read(model_id)
    if model is None:
        return False
    if not model.active:
        return False
    return True