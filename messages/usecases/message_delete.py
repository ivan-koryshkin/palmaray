import attrs
from messages.models import MessageModel
from messages.schemas import MessageSqlFilter

from lib.repo import GenericRepo


@attrs.frozen(kw_only=True, slots=True)
class DeleteOldMessage:
    repo: GenericRepo[MessageModel, MessageSqlFilter]
    max_count: int = 30

    async def __call__(self, topic_id: int, count: int) -> bool:
        messages = await self.repo.list(
            flt=MessageSqlFilter(user_id=0, topic_id=topic_id, tokenized=None, date_from=None, date_to=None, role=None),
            limit=count,
            order_by="created_at",
        )
        if len(messages) > self.max_count:
            ids_to_delete: list[int | str] = [m.id for m in messages]
            return await self.repo.delete_bulk(ids_to_delete)
        return False
