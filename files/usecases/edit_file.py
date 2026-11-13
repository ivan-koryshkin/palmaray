import asyncio

import attrs
from files.workspace import Workspace, WorkspaceError


@attrs.frozen(kw_only=True, slots=True)
class EditFile:
    """Replace text in an existing file. Returns the number of replacements made."""

    workspace: Workspace

    async def __call__(
        self, *, user_id: int, topic_id: int, name: str, old_text: str, new_text: str, replace_all: bool = False
    ) -> int:
        if not old_text:
            raise WorkspaceError("old_text must not be empty")

        path = self.workspace.resolve(user_id, topic_id, name)
        if not path.is_file():
            raise WorkspaceError(f"File '{name}' not found")

        try:
            text = await asyncio.to_thread(path.read_text, encoding="utf-8")
        except UnicodeDecodeError:
            raise WorkspaceError(f"File '{name}' is not a UTF-8 text file") from None

        count = text.count(old_text)
        if count == 0:
            raise WorkspaceError("old_text was not found in the file")
        if count > 1 and not replace_all:
            raise WorkspaceError(
                f"old_text occurs {count} times; add more surrounding context to make it unique or set replace_all"
            )

        updated = text.replace(old_text, new_text) if replace_all else text.replace(old_text, new_text, 1)
        await asyncio.to_thread(path.write_text, updated, encoding="utf-8")
        return count if replace_all else 1
