import attrs
from files.workspace import Workspace, WorkspaceError
from telegram import Bot

TELEGRAM_BOT_DOWNLOAD_LIMIT = 20 * 1024 * 1024


@attrs.frozen(kw_only=True, slots=True)
class DownloadFile:
    """Download a telegram attachment into the user's workspace. Returns the saved file name."""

    bot: Bot
    workspace: Workspace
    max_size: int = TELEGRAM_BOT_DOWNLOAD_LIMIT

    async def __call__(
        self, *, user_id: int, topic_id: int, file_id: str, file_name: str, file_size: int | None = None
    ) -> str:
        if file_size is not None and file_size > self.max_size:
            raise WorkspaceError(f"File is too large ({file_size} bytes, limit is {self.max_size})")

        target = self.workspace.unique_path(user_id, topic_id, file_name)
        tg_file = await self.bot.get_file(file_id)
        await tg_file.download_to_drive(custom_path=target)
        return target.name
