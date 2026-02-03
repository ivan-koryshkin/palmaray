from messages.models import MessageModel
from messages.schemas import MessageSqlFilter
from sqlalchemy import ColumnElement, and_, true
from sqlalchemy.ext.asyncio import AsyncSession

from lib.repo import GenericRepo


def build_message_where(model: MessageModel, flt: MessageSqlFilter | None) -> ColumnElement[bool]:
    if flt is None:
        return true()

    conds: list[ColumnElement[bool]] = []
    if flt.get("topic_id") is not None:
        conds.append(MessageModel.topic_id == flt["topic_id"])
    if flt.get("tokenized") is not None:
        conds.append(MessageModel.tokenized.is_(flt["tokenized"]))
    if flt.get("role") is not None:
        conds.append(MessageModel.role == flt["role"])
    return and_(*conds) if conds else true()


def new_message_repo(session: AsyncSession) -> GenericRepo[MessageModel, MessageSqlFilter]:
    return GenericRepo(model=MessageModel, build_filter=build_message_where, session=session)  # type: ignore[arg-type]
