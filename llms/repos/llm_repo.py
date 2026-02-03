from llms.models import LLMModel
from sqlalchemy import ColumnElement, and_, true

from lib.repo import GenericRepo
from sqlalchemy.ext.asyncio import AsyncSession


class LlmFilters:
    name: str


def build_llm_where(model: LLMModel, flt: LlmFilters | None) -> ColumnElement[bool]:
    if flt is None:
        return true()

    conds: list[ColumnElement[bool]] = []
    if flt.name is not None:
        conds.append(LLMModel.name.ilike(f"%{flt.name}%"))
    return and_(*conds) if conds else true()


def new_llm_repo(session: AsyncSession) -> GenericRepo[LLMModel, LlmFilters]:
    return GenericRepo(model=LLMModel, build_filter=build_llm_where, session=session)  # type: ignore[arg-type]
