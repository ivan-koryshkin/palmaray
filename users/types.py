from typing import TypedDict


class UserSqlFilters(TypedDict):
    name: str


class UserInfo(TypedDict):
    id: int
    selected_model: str
    name: str