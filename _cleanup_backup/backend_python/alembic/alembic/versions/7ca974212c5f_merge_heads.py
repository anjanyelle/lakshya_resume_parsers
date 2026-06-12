"""merge_heads

Revision ID: 7ca974212c5f
Revises: add_model_results, add_summary_manually_edited
Create Date: 2026-04-27 06:52:41.179462

"""
from alembic import op
import sqlalchemy as sa



revision = '7ca974212c5f'
down_revision = ('add_model_results', 'add_summary_manually_edited')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
