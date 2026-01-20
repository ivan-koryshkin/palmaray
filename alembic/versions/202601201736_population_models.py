"""population models

Revision ID: ed75a08e4bf6
Revises: 9bf631a54cbd
Create Date: 2026-01-20 17:36:19.793729

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from llms.types import Provider


# revision identifiers, used by Alembic.
revision: str = 'ed75a08e4bf6'
down_revision: Union[str, Sequence[str], None] = '9bf631a54cbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    op.add_column('llms', sa.Column('provider', sa.String(), nullable=False, server_default=Provider.OPENAI.value))

    insert_sql = sa.text(
        "INSERT INTO llms (id, name, active, is_default, provider) VALUES (:id, :name, :active, :is_default, :provider) ON CONFLICT (id) DO NOTHING"
    )
    models = [
            {'id': 'gpt-5.1', 'name': 'GPT-5.1', 'active': True, 'is_default': False, 'provider': Provider.OPENAI.value},
            {'id': 'gpt-5', 'name': 'GPT-5', 'active': True, 'is_default': False, 'provider': Provider.OPENAI.value},
            {'id': 'gpt-5-mini', 'name': 'GPT-5 mini', 'active': True, 'is_default': False, 'provider': Provider.OPENAI.value},
            {'id': 'gpt-5-nano', 'name': 'GPT-5 nano', 'active': True, 'is_default': True, 'provider': Provider.OPENAI.value},
            {'id': 'gpt-4.1', 'name': 'GPT-4.1', 'active': True, 'is_default': False, 'provider': Provider.OPENAI.value},
            {'id': 'gpt-4.1-mini', 'name': 'GPT-4.1 mini', 'active': True, 'is_default': False, 'provider': Provider.OPENAI.value},
            {'id': 'gpt-4.1-nano', 'name': 'GPT-4.1 nano', 'active': True, 'is_default': False, 'provider': Provider.OPENAI.value},
            {'id': 'o4-mini', 'name': 'O4 mini', 'active': True, 'is_default': False, 'provider': Provider.OPENAI.value},
            {'id': 'o3', 'name': 'O3', 'active': True, 'is_default': False, 'provider': Provider.OPENAI.value},
    ]
    for m in models:
        bind.execute(insert_sql, m)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        "DELETE FROM llms WHERE id IN ('gpt-5.1','gpt-5','gpt-5-mini','gpt-5-nano','gpt-4.1','gpt-4.1-mini','gpt-4.1-nano','o4-mini','o3')"
    )
    op.drop_column('llms', 'provider')
