import asyncio

import attrs
from files.workspace import Workspace


@attrs.frozen(kw_only=True, slots=True)
class ListFiles:
    workspace: Workspace

    async def __call__(self, *, user_id: int, topic_id: int) -> list[tuple[str, int]]:
        base = self.workspace.dir(user_id, topic_id)

        def _list() -> list[tuple[str, int]]:
            return sorted((str(p.relative_to(base)), p.stat().st_size) for p in base.rglob("*") if p.is_file())

        return await asyncio.to_thread(_list)
