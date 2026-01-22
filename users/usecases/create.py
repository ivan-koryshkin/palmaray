import attrs

from lib.repo import GenericRepo
from users.models import UserModel
from users.schemas import UserSqlFilters


@attrs.frozen(kw_only=True, slots=True)
class CreateOrUpdate:
    repo: GenericRepo[UserModel, UserSqlFilters]

    async def __call__(self, id: int, name: str) -> UserModel:
        user = await self.repo.read(id)
        if user and user.name != name:
            user.name = name
            user = await self.repo.update(user)
        else:
            user = await self.repo.create(UserModel(id=id, name=name))
        return user
