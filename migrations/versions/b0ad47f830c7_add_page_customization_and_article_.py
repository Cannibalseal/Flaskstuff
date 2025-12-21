"""Add page customization and article writer permissions

Revision ID: b0ad47f830c7
Revises: 6e0b173ecfbd
Create Date: 2025-12-21 13:02:29.970161

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0ad47f830c7'
down_revision: Union[str, Sequence[str], None] = '6e0b173ecfbd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('can_write_articles', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('custom_bg_color', sa.String(length=20), nullable=True, server_default='#0a0e27'))
        batch_op.add_column(sa.Column('custom_text_color', sa.String(length=20), nullable=True, server_default='#e2e8f0'))
        batch_op.add_column(sa.Column('custom_accent_color', sa.String(length=20), nullable=True, server_default='#06b6d4'))
        batch_op.add_column(sa.Column('custom_font_size', sa.String(length=10), nullable=True, server_default='16px'))
        batch_op.add_column(sa.Column('custom_font_family', sa.String(length=100), nullable=True, server_default='system-ui'))


def downgrade() -> None:
    """Downgrade schema."""
    # Use batch mode for SQLite compatibility
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('custom_font_family')
        batch_op.drop_column('custom_font_size')
        batch_op.drop_column('custom_accent_color')
        batch_op.drop_column('custom_text_color')
        batch_op.drop_column('custom_bg_color')
        batch_op.drop_column('can_write_articles')
