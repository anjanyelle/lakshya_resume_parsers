"""add_candidate_achievements

Revision ID: 004_candidate_achievements
Revises: 003_years_experience_conf
Create Date: 2026-02-12
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "004_candidate_achievements"
down_revision = "003_years_experience_conf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "candidate_achievements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_candidate_achievements_candidate_id",
        "candidate_achievements",
        ["candidate_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_candidate_achievements_candidate_id", table_name="candidate_achievements"
    )
    op.drop_table("candidate_achievements")
