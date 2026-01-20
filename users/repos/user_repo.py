from sqlalchemy import ColumnElement, and_, true
from sqlalchemy.ext.asyncio import AsyncSession

from lib.repo import GenericRepo
from users.models import UserModel
from users.types import UserSqlFilters


def build_user_where(model: UserModel, flt: UserSqlFilters | None) -> ColumnElement[bool]:
    conds: list[ColumnElement[bool]] = []
    if flt.name is not None:
        conds.append(UserModel.name.ilike(f"%{flt.name}%"))
    return and_(*conds) if conds else true()


def new_user_repo(session: AsyncSession) -> GenericRepo[UserModel, UserSqlFilters]:
    return GenericRepo(model=UserModel, build_filter=build_user_where, session=session)
