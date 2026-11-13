import asyncio

import attrs
from files.workspace import Workspace, WorkspaceError


@attrs.frozen(kw_only=True, slots=True)
class WriteFile:
    """Create a new text file or fully overwrite an existing one. Returns bytes written."""

    workspace: Workspace
    max_size: int = 5 * 1024 * 1024

    async def __call__(self, *, user_id: int, topic_id: int, name: str, content: str) -> int:
        data = content.encode("utf-8")
        if len(data) > self.max_size:
            raise WorkspaceError(f"Content is too large ({len(data)} bytes, limit is {self.max_size})")

        path = self.workspace.resolve(user_id, topic_id, name)
        path.parent.mkdir(parents=True, exist_ok=True)
        await asyncio.to_thread(path.write_bytes, data)
        return len(data)
