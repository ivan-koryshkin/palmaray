import attrs

from collections.abc import Callable

@attrs.frozen(kw_only=True, slots=True)
class ReadLongHistory:
    tokenize: Callable[[str], list[float]]

    def __call__(self, user_id: int, topic_id: int, last_message: str) -> list:
        return []