from pgvector.sqlalchemy import Vector
from sqlalchemy import BigInteger, Boolean, ForeignKey, ForeignKeyConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from lib.models import Base
from lib.sqlalchemy_encrypted import EncryptedType


class TopicModel(Base):
    __tablename__ = "topics"

    # telegram thread ids are not unique across users (private chats all use 0), so a topic is (user_id, id)
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)


class MessageModel(Base):
    __tablename__ = "messages"
    __table_args__ = (
        ForeignKeyConstraint(["user_id", "topic_id"], ["topics.user_id", "topics.id"], name="messages_user_topic_fkey"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    chat_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    text: Mapped[str] = mapped_column(EncryptedType(), nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    tokenized: Mapped[str] = mapped_column(Boolean, nullable=False, default=False)
    topic_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "message": self.text}

    def to_str(self) -> str:
        return f"{self.role}: {self.text}"


class TopicEmbedModel(Base):
    __tablename__ = "topic_embeddings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id", "topic_id"], ["topics.user_id", "topics.id"], name="topic_embeddings_user_topic_fkey"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    topic_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    chunk: Mapped[str] = mapped_column(EncryptedType(), nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536), nullable=False)
    user_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True, index=True)
    image_url: Mapped[str | None] = mapped_column(String, nullable=True)
