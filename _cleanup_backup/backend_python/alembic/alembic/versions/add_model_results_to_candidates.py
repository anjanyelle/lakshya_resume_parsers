"""add model_results to candidates

Revision ID: add_model_results
Revises: 
Create Date: 2026-04-13

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision = 'add_model_results'
down_revision = None  # Update this with the actual previous revision ID
branch_labels = None
depends_on = None


def upgrade():
    # Add model_results column to candidates table
    op.add_column('candidates', sa.Column('model_results', JSONB, nullable=True))


def downgrade():
    # Remove model_results column from candidates table
    op.drop_column('candidates', 'model_results')
