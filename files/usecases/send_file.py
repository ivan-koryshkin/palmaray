import attrs
from files.workspace import Workspace, WorkspaceError
from telegram import Bot


@attrs.frozen(kw_only=True, slots=True)
class SendFile:
    """Send a file from the user's workspace back to the telegram chat."""

    bot: Bot
    workspace: Workspace

    async def __call__(
        self, *, user_id: int, chat_id: int, topic_id: int, name: str, caption: str | None = None
    ) -> None:
        path = self.workspace.resolve(user_id, topic_id, name)
        if not path.is_file():
            raise WorkspaceError(f"File '{name}' not found")

        with path.open("rb") as fh:
            await self.bot.send_document(
                chat_id=chat_id,
                message_thread_id=topic_id or None,
                document=fh,
                filename=path.name,
                caption=caption,
            )
