"""topic embeddings user_id

Revision ID: 7c1e4a9d52b3
Revises: 0ad903781722
Create Date: 2026-11-13 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "7c1e4a9d52b3"
down_revision: Union[str, Sequence[str], None] = "0ad903781722"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("topic_embeddings", sa.Column("user_id", sa.BigInteger(), nullable=True))
    op.create_index("ix_topic_embeddings_user_id", "topic_embeddings", ["user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_topic_embeddings_user_id", table_name="topic_embeddings")
    op.drop_column("topic_embeddings", "user_id")
