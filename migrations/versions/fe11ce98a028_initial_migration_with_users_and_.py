"""Initial migration with users and articles

Revision ID: fe11ce98a028
Revises: 
Create Date: 2025-12-19 14:19:34.601073

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fe11ce98a028'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    try:
        op.create_table(
            'users',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('username', sa.String(length=80), nullable=False),
            sa.Column('password_hash', sa.String(length=200), nullable=False),
            sa.Column('is_admin', sa.Integer(), nullable=False),
            sa.Column('must_change_password', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('username')
        )
    except:
        pass  # Table already exists
    
    # Create articles table
    try:
        op.create_table(
            'articles',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('slug', sa.String(length=200), nullable=False),
            sa.Column('title', sa.String(length=200), nullable=False),
            sa.Column('summary', sa.Text(), nullable=True),
            sa.Column('content', sa.Text(), nullable=True),
            sa.Column('published', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('slug')
        )
        op.create_index(op.f('ix_articles_slug'), 'articles', ['slug'], unique=True)
        op.create_index(op.f('ix_articles_published'), 'articles', ['published'], unique=False)
    except:
        pass  # Table already exists
    
    # Create newsletter table
    try:
        op.create_table(
            'newsletter',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('email', sa.String(length=120), nullable=False),
            sa.Column('subscribed_at', sa.DateTime(), nullable=False),
            sa.Column('is_active', sa.Integer(), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('email')
        )
        op.create_index(op.f('ix_newsletter_email'), 'newsletter', ['email'], unique=True)
    except:
        pass  # Table already exists


def downgrade() -> None:
    """Downgrade schema."""
    try:
        op.drop_index(op.f('ix_articles_published'), table_name='articles')
        op.drop_index(op.f('ix_articles_slug'), table_name='articles')
        op.drop_table('newsletter')
        op.drop_table('articles')
        op.drop_table('users')
    except:
        pass
