from messages.models import MessageModel
from messages.types import MessageSqlFilter
from sqlalchemy import ColumnElement, and_, true
from sqlalchemy.ext.asyncio import AsyncSession

from lib.repo import GenericRepo


def build_message_where(model: MessageModel, flt: MessageSqlFilter | None) -> ColumnElement[bool]:
    conds: list[ColumnElement[bool]] = []
    if flt["topic_id"] is not None:
        conds.append(MessageModel.topic_id == flt["topic_id"])
    if flt["tokenized"] is not None:
        conds.append(MessageModel.tokenized.is_(flt["tokenized"]))
    if flt["role"] is not None:
        conds.append(MessageModel.role == flt["role"])
    return and_(*conds) if conds else true()


def new_message_repo(session: AsyncSession) -> GenericRepo[MessageModel, MessageSqlFilter]:
    return GenericRepo(model=MessageModel, build_filter=build_message_where, session=session)
