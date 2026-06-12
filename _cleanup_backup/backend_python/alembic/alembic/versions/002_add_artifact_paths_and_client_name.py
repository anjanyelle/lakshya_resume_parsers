"""add_artifact_paths_and_client_name

Revision ID: 002_artifact_paths_client
Revises: 001_initial_schema
Create Date: 2026-02-09
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "002_artifact_paths_client"
down_revision = "001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "parsing_jobs",
        sa.Column("original_file_copy_path", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "parsing_jobs",
        sa.Column("extracted_text_path", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "parsing_jobs",
        sa.Column("parsed_json_path", sa.String(length=500), nullable=True),
    )

    op.add_column(
        "work_history",
        sa.Column("client_name", sa.String(length=200), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("work_history", "client_name")
    op.drop_column("parsing_jobs", "parsed_json_path")
    op.drop_column("parsing_jobs", "extracted_text_path")
    op.drop_column("parsing_jobs", "original_file_copy_path")
