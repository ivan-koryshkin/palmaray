import attrs
from messages.models import TopicModel
from messages.types import TopicSqlFilter

from lib.repo import GenericRepo


@attrs.frozen(kw_only=True, slots=True)
class SaveTopic:
    repo: GenericRepo[TopicModel, TopicSqlFilter]

    async def __call__(self, id: int, name: str, user_id: int) -> int:
        topic = await self.repo.read(id)
        if topic is not None:
            return topic.id

        topic = await self.repo.create(TopicModel(id=id, name=name, user_id=user_id))
        return topic.id
