import asyncio

import attrs
from files.workspace import Workspace, WorkspaceError


@attrs.frozen(kw_only=True, slots=True)
class ReadText:
    """Read a whole UTF-8 text file from the workspace (no truncation)."""

    workspace: Workspace

    async def __call__(self, *, user_id: int, topic_id: int, name: str) -> str:
        path = self.workspace.resolve(user_id, topic_id, name)
        if not path.is_file():
            raise WorkspaceError(f"File '{name}' not found")
        try:
            return await asyncio.to_thread(path.read_text, encoding="utf-8")
        except UnicodeDecodeError:
            raise WorkspaceError(f"File '{name}' is not a UTF-8 text file") from None
