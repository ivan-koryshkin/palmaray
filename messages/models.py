from lib.models import Base
from sqlalchemy import Boolean, String, BigInteger, ForeignKey, Integer
from pgvector.sqlalchemy import Vector
from sqlalchemy.orm import Mapped, mapped_column


class TopicModel(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))


class MessageModel(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    tokenized: Mapped[str] = mapped_column(Boolean, nullable=False, default=False)
    topic_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("topics.id"))

    def to_dict(self) -> dict[str, str]:
        return {
            "role": self.role,
            "message": self.text
        }
    
    def to_str(self) -> str:
        return f"{self.role}: {self.text}"


class TopicEmbedModel(Base):
    __tablename__ = "topic_embeddings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("topics.id"), nullable=False)
    chunk: Mapped[str] = mapped_column(String, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
