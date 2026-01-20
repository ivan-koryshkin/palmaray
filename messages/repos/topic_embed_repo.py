from typing import Tuple, Union

from messages.models import TopicEmbedModel
from messages.types import TopicEmbedSqlFilter
from sqlalchemy import ColumnElement, and_, bindparam, true
from sqlalchemy.ext.asyncio import AsyncSession

from lib.repo import GenericRepo


def build_topic_embed_where(
    model: TopicEmbedModel, flt: TopicEmbedSqlFilter | None
) -> Union[ColumnElement[bool], Tuple[ColumnElement[bool], ColumnElement[float]]]:
    conds: list[ColumnElement[bool]] = []
    distance_expr = None
    for k, v in (flt or {}).items():
        if v is None:
            continue
        if k == "embedding":
            distance_expr = TopicEmbedModel.embedding.op("<->")(bindparam("emb"))
            continue
        if hasattr(model, k):
            conds.append(getattr(model, k) == v)
    where = and_(*conds) if conds else true()
    if distance_expr is not None:
        return where, distance_expr
    return where


def new_topic_embed_repo(session: AsyncSession) -> GenericRepo[TopicEmbedModel, TopicEmbedSqlFilter]:
    return GenericRepo(
        model=TopicEmbedModel,
        build_filter=build_topic_embed_where,
        session=session,
    )
