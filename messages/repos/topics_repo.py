from messages.models import TopicModel
from messages.schemas import TopicSqlFilter
from sqlalchemy import ColumnElement, and_, true
from sqlalchemy.ext.asyncio import AsyncSession

from lib.repo import GenericRepo


def build_topic_where(model: TopicModel, flt: TopicSqlFilter | None) -> ColumnElement[bool]:
    if flt is None:
        return true()

    conds: list[ColumnElement[bool]] = []
    if flt.get("chat_id") is not None:
        conds.append(TopicModel.chat_id == flt["chat_id"])
    return and_(*conds) if conds else true()


def new_topic_repo(session: AsyncSession) -> GenericRepo[TopicModel, TopicSqlFilter]:
    return GenericRepo(model=TopicModel, build_filter=build_topic_where, session=session)  # type: ignore[arg-type]
