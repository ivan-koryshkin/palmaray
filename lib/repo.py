from collections.abc import Callable
from typing import Any, Generic, Mapping, Type, TypeVar

import attrs
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import ColumnElement

TModel = TypeVar("TModel")
TFilter = TypeVar("TFilter")

PK_TYPE = int | str


@attrs.frozen(kw_only=True, slots=True)
class GenericRepo(Generic[TModel, TFilter]):
    model: Type[TModel]
    build_filter: Callable[[Type[TModel], Mapping[str, Any]], ColumnElement[bool]]
    session: AsyncSession

    async def create(self, model: TModel) -> TModel:
        self.session.add(model)
        await self.session.flush()
        return model

    async def create_bulk(self, models: list[TModel]) -> list[TModel]:
        if not models:
            return []

        self.session.add_all(models)
        await self.session.flush()
        return models

    async def read(self, id: PK_TYPE) -> TModel | None:
        stmt = select(self.model).where(getattr(self.model, "id") == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, model: TModel) -> TModel:
        merged = await self.session.merge(model)
        await self.session.flush()
        return merged

    async def delete(self, id: PK_TYPE) -> bool:
        obj = await self.session.get(self.model, id)
        if obj is None:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def delete_bulk(self, ids: list[PK_TYPE]) -> bool:
        if not ids:
            return False
        stmt = delete(self.model).where(getattr(self.model, "id").in_(ids))
        result = await self.session.execute(stmt)
        return bool(result.rowcount) if hasattr(result, "rowcount") else True

    async def count(self, flt: TFilter | None = None) -> int:
        stmt = select(func.count()).select_from(self.model)
        filter_dict = flt if isinstance(flt, dict) else {}
        for k, v in filter_dict.items():
            if hasattr(self.model, k):
                stmt = stmt.where(getattr(self.model, k) == v)
        result = await self.session.execute(stmt)
        return int(result.scalar_one())

    async def list(
        self,
        flt: TFilter | None = None,
        limit: int | None = None,
        order_by: str | None = None,
    ) -> list[TModel]:
        stmt = select(self.model)
        filter_dict = flt if isinstance(flt, dict) else {}
        for k, v in filter_dict.items():
            if hasattr(self.model, k):
                stmt = stmt.where(getattr(self.model, k) == v)
        if order_by is not None and hasattr(self.model, order_by):
            stmt = stmt.order_by(getattr(self.model, order_by))
        if limit is not None:
            stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
