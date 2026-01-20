import attrs
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from messages.models import MessageModel
from messages.types import MessageSqlFilter, RoleEnum

from lib.repo import GenericRepo


@attrs.frozen(kw_only=True, slots=True)
class ReadShortHistory:
    repo: GenericRepo[MessageModel, MessageSqlFilter]

    async def __call__(self, user_id: int, topic_id: int) -> list[BaseMessage]:
        messages = await self.repo.list(
            flt={"user_id": user_id, "topic_id": topic_id, "limit": 5, "order_by": "created_at"}
        )
        result: list[BaseMessage] = []
        for message in messages:
            if message.role == RoleEnum.USER.name:
                msg = AIMessage(content=message.text)
            else:
                msg = HumanMessage(content=message.text)
            result.append(msg)
        return result
