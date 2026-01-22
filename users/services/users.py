from sqlalchemy.ext.asyncio import AsyncSession

from lib.database import atomic
from users.repos.user_repo import new_user_repo
from users.schemas import UserInfo
from users.usecases.create import CreateOrUpdate


@atomic
async def user_create(session: AsyncSession, id: int, name: str) -> bool:
    repo = new_user_repo(session=session)
    create_update_user = CreateOrUpdate(repo=repo)
    await create_update_user(id, name)


async def get_user_info(session: AsyncSession, user_id: int) -> UserInfo:
    repo = new_user_repo(session)
    user_db = await repo.read(user_id)
    return {"id": user_db.id, "name": user_db.name, "selected_model": user_db.selected_model}


async def set_user_selected_model(session: AsyncSession, user_id: int, model_id: str) -> bool:
    repo = new_user_repo(session)
    user_db = await repo.read(user_id)
    if not user_db:
        return False

    user_db.selected_model = model_id
    await repo.update(user_db)
