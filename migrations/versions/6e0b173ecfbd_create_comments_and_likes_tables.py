"""Create comments and likes tables

Revision ID: 6e0b173ecfbd
Revises: 20602c9cdc1d
Create Date: 2025-12-21 12:33:43.470373

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e0b173ecfbd'
down_revision: Union[str, Sequence[str], None] = '20602c9cdc1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create comments table if it doesn't exist
    try:
        op.create_table(
            'comments',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('approved', sa.Boolean(), nullable=False),
            sa.Column('article_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
    except:
        pass  # Table already exists
    
    # Create likes table if it doesn't exist
    try:
        op.create_table(
            'likes',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('article_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('article_id', 'user_id', name='unique_article_like')
        )
    except:
        pass  # Table already exists


def downgrade() -> None:
    """Downgrade schema."""
    try:
        op.drop_table('likes')
    except:
        pass
    
    try:
        op.drop_table('comments')
    except:
        pass
    pass
    # ### end Alembic commands ###
