import re
from pathlib import Path

import attrs


class WorkspaceError(Exception):
    """Base error for everything that goes wrong while working with user files."""


@attrs.frozen(slots=True)
class Workspace:
    """Per user/topic sandbox on local disk (default: /tmp/palmaray/<user_id>/<topic_id>)."""

    root: Path

    def dir(self, user_id: int, topic_id: int) -> Path:
        path = (self.root / str(user_id) / str(topic_id)).resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path

    def resolve(self, user_id: int, topic_id: int, name: str) -> Path:
        """Resolve a user-supplied relative path, refusing anything that escapes the sandbox."""
        base = self.dir(user_id, topic_id)
        if not name or not name.strip():
            raise WorkspaceError("File name is empty")
        target = (base / name).resolve()
        if target == base or not target.is_relative_to(base):
            raise WorkspaceError(f"Path '{name}' is outside of the workspace")
        return target

    def unique_path(self, user_id: int, topic_id: int, file_name: str) -> Path:
        """Sanitized path for a new incoming file; never overwrites an existing one."""
        safe = re.sub(r"[^\w.\- ]", "_", Path(file_name).name).strip(" .") or "file"
        base = self.dir(user_id, topic_id)
        candidate = base / safe
        stem, suffix = candidate.stem, candidate.suffix
        counter = 1
        while candidate.exists():
            candidate = base / f"{stem}_{counter}{suffix}"
            counter += 1
        return candidate
