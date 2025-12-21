"""Add SiteSettings table for admin customization

Revision ID: ae7eec2f994b
Revises: 5c5339a0bd05
Create Date: 2025-12-21 13:28:52.033699

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae7eec2f994b'
down_revision: Union[str, Sequence[str], None] = '5c5339a0bd05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create site_settings table if it doesn't exist
    try:
        op.create_table(
            'site_settings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('site_name', sa.String(length=100), nullable=True),
            sa.Column('site_tagline', sa.String(length=200), nullable=True),
            sa.Column('site_description', sa.Text(), nullable=True),
            sa.Column('welcome_page_content', sa.Text(), nullable=True),
            sa.Column('about_page_content', sa.Text(), nullable=True),
            sa.Column('footer_content', sa.Text(), nullable=True),
            sa.Column('custom_css', sa.Text(), nullable=True),
            sa.Column('custom_js', sa.Text(), nullable=True),
            sa.Column('meta_keywords', sa.String(length=500), nullable=True),
            sa.Column('meta_description', sa.String(length=500), nullable=True),
            sa.Column('site_twitter', sa.String(length=100), nullable=True),
            sa.Column('site_github', sa.String(length=100), nullable=True),
            sa.Column('site_email', sa.String(length=100), nullable=True),
            sa.Column('primary_color', sa.String(length=20), nullable=True),
            sa.Column('secondary_color', sa.String(length=20), nullable=True),
            sa.Column('logo_path', sa.String(length=255), nullable=True),
            sa.Column('favicon_path', sa.String(length=255), nullable=True),
            sa.Column('enable_comments', sa.Boolean(), nullable=True),
            sa.Column('enable_likes', sa.Boolean(), nullable=True),
            sa.Column('enable_newsletter', sa.Boolean(), nullable=True),
            sa.Column('enable_social_sharing', sa.Boolean(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
    except:
        pass  # Table already exists


def downgrade() -> None:
    """Downgrade schema."""
    try:
        op.drop_table('site_settings')
    except:
        pass  # Table doesn't exist
