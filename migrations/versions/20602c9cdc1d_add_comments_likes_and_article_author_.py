"""Add comments, likes, and article author tracking

Revision ID: 20602c9cdc1d
Revises: 9f56e6cc93ce
Create Date: 2025-12-21 12:33:02.481294

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20602c9cdc1d'
down_revision: Union[str, Sequence[str], None] = '9f56e6cc93ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Use batch mode for SQLite
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('author_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_articles_author', 'users', ['author_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Use batch mode for SQLite
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.drop_constraint('fk_articles_author', type_='foreignkey')
        batch_op.drop_column('author_id')
