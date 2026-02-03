from collections.abc import Callable

import attrs
from messages.models import MessageModel
from messages.schemas import MessageSqlFilter, RoleEnum

from lib.repo import GenericRepo


@attrs.frozen(kw_only=True, slots=True)
class SaveMessage:
    repo: GenericRepo[MessageModel, MessageSqlFilter]
    encrypt_message: Callable[[str], str]

    async def __call__(
        self, *, message_id: int, chat_id: int, text: str, topic_id: int, role: RoleEnum, image_url: str | None = None
    ) -> int | None:
        msg = await self.repo.read(message_id)
        if msg is not None:
            return None

        encrypted = self.encrypt_message(text)

        msg = await self.repo.create(
            MessageModel(
                id=message_id, chat_id=chat_id, text=encrypted, role=role.value, topic_id=topic_id, image_url=image_url
            )
        )
        return msg.id
