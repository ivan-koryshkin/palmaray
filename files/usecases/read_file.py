import asyncio

import attrs
from files.workspace import Workspace, WorkspaceError


@attrs.frozen(kw_only=True, slots=True)
class ReadFile:
    workspace: Workspace
    max_chars: int = 50_000

    async def __call__(self, *, user_id: int, topic_id: int, name: str, offset: int = 0) -> str:
        path = self.workspace.resolve(user_id, topic_id, name)
        if not path.is_file():
            raise WorkspaceError(f"File '{name}' not found")

        try:
            text = await asyncio.to_thread(path.read_text, encoding="utf-8")
        except UnicodeDecodeError:
            raise WorkspaceError(f"File '{name}' is not a UTF-8 text file") from None

        chunk = text[offset : offset + self.max_chars]
        end = offset + len(chunk)
        if end < len(text):
            chunk += f"\n[truncated: showing chars {offset}-{end} of {len(text)}; call again with offset={end}]"
        return chunk
