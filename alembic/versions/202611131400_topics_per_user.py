"""topics per user

Telegram thread id 0 (private chats) is the same for every user, so topics.id alone cannot be the primary key.
The key becomes (user_id, id) and messages / topic_embeddings reference it with (user_id, topic_id).
Rows with user_id NULL (legacy) are not checked by the composite foreign key (MATCH SIMPLE).

Revision ID: 9d2a7c5e1b64
Revises: 3b8f6d1e9a40
Create Date: 2026-11-13 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9d2a7c5e1b64"
down_revision: Union[str, Sequence[str], None] = "3b8f6d1e9a40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint("messages_topic_id_fkey", "messages", type_="foreignkey")
    op.drop_constraint("topic_embeddings_topic_id_fkey", "topic_embeddings", type_="foreignkey")
    op.drop_constraint("topics_pkey", "topics", type_="primary")
    op.create_primary_key("topics_pkey", "topics", ["user_id", "id"])

    # every (user, topic) pair that already owns data must have its own topic row before the new FKs
    op.execute("""
        INSERT INTO topics (id, user_id, name)
        SELECT DISTINCT topic_id, user_id, 'default topic ' || topic_id
        FROM (
            SELECT topic_id, user_id FROM messages WHERE user_id IS NOT NULL
            UNION
            SELECT topic_id, user_id FROM topic_embeddings WHERE user_id IS NOT NULL
        ) AS pairs
        ON CONFLICT DO NOTHING
        """)

    op.create_foreign_key("messages_user_topic_fkey", "messages", "topics", ["user_id", "topic_id"], ["user_id", "id"])
    op.create_foreign_key(
        "topic_embeddings_user_topic_fkey", "topic_embeddings", "topics", ["user_id", "topic_id"], ["user_id", "id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("topic_embeddings_user_topic_fkey", "topic_embeddings", type_="foreignkey")
    op.drop_constraint("messages_user_topic_fkey", "messages", type_="foreignkey")
    # a single-column key cannot hold the same topic id for several users: keep the oldest row of each id
    op.execute("""
        DELETE FROM topics t USING topics o
        WHERE t.id = o.id AND (t.created_at, t.user_id) > (o.created_at, o.user_id)
        """)
    op.drop_constraint("topics_pkey", "topics", type_="primary")
    op.create_primary_key("topics_pkey", "topics", ["id"])
    op.create_foreign_key("messages_topic_id_fkey", "messages", "topics", ["topic_id"], ["id"])
    op.create_foreign_key("topic_embeddings_topic_id_fkey", "topic_embeddings", "topics", ["topic_id"], ["id"])
