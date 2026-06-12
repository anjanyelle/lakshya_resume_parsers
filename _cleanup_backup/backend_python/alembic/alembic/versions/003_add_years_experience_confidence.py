"""add_years_experience_confidence

Revision ID: 003_years_experience_conf
Revises: 002_artifact_paths_client
Create Date: 2026-02-12
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003_years_experience_conf"
down_revision = "002_artifact_paths_client"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "candidates",
        sa.Column("years_experience_confidence", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("candidates", "years_experience_confidence")
