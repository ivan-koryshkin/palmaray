from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from lib.models import Base
from .schemas import Provider


class LLMModel(Base):
    __tablename__ = "llms"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    provider: Mapped[str] = mapped_column(String, nullable=False, default=Provider.OPENAI.value)
