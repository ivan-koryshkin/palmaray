from messages.models import TopicEmbedModel
from messages.schemas import TopicEmbedSqlFilter
import attrs
from sqlalchemy import ColumnElement, and_, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from lib.repo import GenericRepo


def build_topic_embed_where(model: TopicEmbedModel, flt: TopicEmbedSqlFilter | None) -> ColumnElement[bool]:
    if flt is None:
        return true()

    conds: list[ColumnElement[bool]] = []
    for k, v in flt.items():
        if k != "embedding" and v is not None and hasattr(model, k):
            conds.append(getattr(model, k) == v)
    return and_(*conds) if conds else true()


@attrs.frozen(kw_only=True, slots=True)
class SearchTopicEmbeds:
    """Nearest chunks of the vector memory, strictly limited to one user."""

    session: AsyncSession

    async def __call__(self, *, user_id: int, embedding: list[float], limit: int) -> list[TopicEmbedModel]:
        stmt = (
            select(TopicEmbedModel)
            .where(TopicEmbedModel.user_id == user_id)
            .order_by(TopicEmbedModel.embedding.l2_distance(embedding))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


def new_topic_embed_search(session: AsyncSession) -> SearchTopicEmbeds:
    return SearchTopicEmbeds(session=session)


def new_topic_embed_repo(session: AsyncSession) -> GenericRepo[TopicEmbedModel, TopicEmbedSqlFilter]:
    return GenericRepo(
        model=TopicEmbedModel,
        build_filter=build_topic_embed_where,  # type: ignore[arg-type]
        session=session,
    )
