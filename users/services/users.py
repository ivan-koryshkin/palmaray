from sqlalchemy.ext.asyncio import AsyncSession
from lib.database import atomic
from users.repos.user_repo import new_user_repo
from users.usecases.create import CreateOrUpdate


@atomic
async def user_create(session: AsyncSession, id: int, name: str) -> bool:
    repo = new_user_repo(session=session)
    create_update_user = CreateOrUpdate(repo=repo)
    await create_update_user(id, name)