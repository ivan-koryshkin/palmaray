"""messages user_id

Existing rows keep user_id NULL on purpose: telegram topic id 0 (private chats) was shared by all users,
so the real owner of old messages cannot be restored. NULL rows are never returned to anyone.

Revision ID: 3b8f6d1e9a40
Revises: 7c1e4a9d52b3
Create Date: 2026-11-13 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "3b8f6d1e9a40"
down_revision: Union[str, Sequence[str], None] = "7c1e4a9d52b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("messages", sa.Column("user_id", sa.BigInteger(), nullable=True))
    op.create_index("ix_messages_user_id", "messages", ["user_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_messages_user_id", table_name="messages")
    op.drop_column("messages", "user_id")
