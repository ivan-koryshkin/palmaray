from functools import wraps
from typing import Any, Awaitable, Callable

from files.usecases.protocols import IEditFile, IListFiles, IReadFile, ISendFile, IWriteFile
from files.workspace import WorkspaceError
from langchain_core.tools import BaseTool, StructuredTool


def _safe(fn: Callable[..., Awaitable[str]]) -> Callable[..., Awaitable[str]]:
    """Turn expected failures into text so the model can react instead of the whole request crashing."""

    @wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            return await fn(*args, **kwargs)
        except (WorkspaceError, OSError) as exc:
            return f"Error: {exc}"

    return wrapper


def build_file_tools(
    *,
    user_id: int,
    chat_id: int,
    topic_id: int,
    list_files: IListFiles,
    read_file: IReadFile,
    write_file: IWriteFile,
    edit_file: IEditFile,
    send_file: ISendFile,
) -> list[BaseTool]:
    @_safe
    async def list_files_tool() -> str:
        files = await list_files(user_id=user_id, topic_id=topic_id)
        if not files:
            return "Workspace is empty"
        return "\n".join(f"{name} ({size} bytes)" for name, size in files)

    @_safe
    async def read_file_tool(name: str, offset: int = 0) -> str:
        return await read_file(user_id=user_id, topic_id=topic_id, name=name, offset=offset)

    @_safe
    async def write_file_tool(name: str, content: str) -> str:
        size = await write_file(user_id=user_id, topic_id=topic_id, name=name, content=content)
        return f"Wrote {size} bytes to {name}"

    @_safe
    async def edit_file_tool(name: str, old_text: str, new_text: str, replace_all: bool = False) -> str:
        n = await edit_file(
            user_id=user_id,
            topic_id=topic_id,
            name=name,
            old_text=old_text,
            new_text=new_text,
            replace_all=replace_all,
        )
        return f"Replaced {n} occurrence(s) in {name}"

    @_safe
    async def send_file_tool(name: str, caption: str | None = None) -> str:
        await send_file(user_id=user_id, chat_id=chat_id, topic_id=topic_id, name=name, caption=caption)
        return f"File {name} was sent to the user"

    return [
        StructuredTool.from_function(
            coroutine=list_files_tool,
            name="list_files",
            description="List files in the user's workspace (files received from the user and files you created).",
        ),
        StructuredTool.from_function(
            coroutine=read_file_tool,
            name="read_file",
            description=(
                "Read a UTF-8 text file from the workspace. Long files are truncated; "
                "use offset (in characters) to read the next part."
            ),
        ),
        StructuredTool.from_function(
            coroutine=write_file_tool,
            name="write_file",
            description="Create a new text file in the workspace or fully overwrite an existing one.",
        ),
        StructuredTool.from_function(
            coroutine=edit_file_tool,
            name="edit_file",
            description=(
                "Edit an existing text file by replacing old_text with new_text. old_text must match exactly "
                "and be unique in the file unless replace_all is true. Read the file first."
            ),
        ),
        StructuredTool.from_function(
            coroutine=send_file_tool,
            name="send_file",
            description="Send a file from the workspace to the user in the telegram chat.",
        ),
    ]
