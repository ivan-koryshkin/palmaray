import attrs

from lib.repo import GenericRepo
from messages.models import MessageModel
from messages.types import MessageSqlFilter

@attrs.frozen(kw_only=True, slots=True)
class DeleteOldMessage:
    max_count = 15
    repo: GenericRepo[MessageModel, MessageSqlFilter]
    
    async def __call__(self, topic_id: int, count: int) -> bool:
        message_models = await self.repo.list(
            flt={"topic_id": topic_id},
            limit=count,
            order_by="created_at"
        )
        if len(message_models) > self.max_count:    
            message_ids = [m.id for m in message_models]
            await self.repo.delete_bulk(message_ids)
