"""Add salary fields to candidates table

Revision ID: 005_add_salary_fields
Revises: 7ca974212c5f
Create Date: 2026-05-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005_add_salary_fields'
down_revision: Union[str, None] = '7ca974212c5f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add expected_salary_min column
    op.add_column('candidates', sa.Column('expected_salary_min', sa.Float(), nullable=True))
    
    # Add expected_salary_max column
    op.add_column('candidates', sa.Column('expected_salary_max', sa.Float(), nullable=True))


def downgrade() -> None:
    # Remove expected_salary_max column
    op.drop_column('candidates', 'expected_salary_max')
    
    # Remove expected_salary_min column
    op.drop_column('candidates', 'expected_salary_min')
