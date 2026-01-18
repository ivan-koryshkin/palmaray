import attrs

from lib.repo import GenericRepo
from messages.models import MessageModel
from messages.types import MessageSqlFilter, RoleEnum
from collections.abc import Callable

@attrs.frozen(kw_only=True, slots=True)
class SaveMessage:
    repo: GenericRepo[MessageModel, MessageSqlFilter]
    encrypt_message: Callable[[str], str]

    async def __call__(
        self, *, 
        message_id: int, 
        chat_id: int, 
        text: str, 
        topic_id: int,
        role: RoleEnum
    ) -> int:
        msg = await self.repo.read(message_id)
        if msg is not None:
            return

        encrypted = self.encrypt_message(text)

        msg = await self.repo.create(
            MessageModel(
                id=message_id,
                chat_id=chat_id,
                text=encrypted,
                role=role.value,
                topic_id=topic_id
            )
        )
        return msg.id