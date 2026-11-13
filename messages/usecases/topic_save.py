import attrs
from messages.models import TopicModel
from messages.schemas import TopicSqlFilter

from lib.repo import GenericRepo


@attrs.frozen(kw_only=True, slots=True)
class SaveTopic:
    repo: GenericRepo[TopicModel, TopicSqlFilter]

    async def __call__(self, id: int, name: str, user_id: int) -> int:
        existing = await self.repo.list(flt=TopicSqlFilter(id=id, user_id=user_id), limit=1)
        if existing:
            return existing[0].id

        topic = await self.repo.create(TopicModel(id=id, name=name, user_id=user_id))
        return topic.id
