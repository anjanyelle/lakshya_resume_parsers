"""initial_schema

Revision ID: 001_initial_schema
Revises:
Create Date: 2026-02-02
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()

    candidate_status_enum = postgresql.ENUM(
        "pending", "processing", "success", "failed", name="candidate_status"
    )
    parsing_job_status_enum = postgresql.ENUM(
        "pending", "processing", "success", "failed", name="parsing_job_status"
    )
    proficiency_level_enum = postgresql.ENUM(
        "beginner", "intermediate", "advanced", "expert", name="proficiency_level"
    )
    review_status_enum = postgresql.ENUM(
        "pending", "in_review", "approved", "rejected", name="review_status"
    )

    candidate_status_enum.create(bind, checkfirst=True)
    parsing_job_status_enum.create(bind, checkfirst=True)
    proficiency_level_enum.create(bind, checkfirst=True)
    review_status_enum.create(bind, checkfirst=True)

    candidate_status_type = postgresql.ENUM(
        "pending",
        "processing",
        "success",
        "failed",
        name="candidate_status",
        create_type=False,
    )
    parsing_job_status_type = postgresql.ENUM(
        "pending",
        "processing",
        "success",
        "failed",
        name="parsing_job_status",
        create_type=False,
    )
    proficiency_level_type = postgresql.ENUM(
        "beginner",
        "intermediate",
        "advanced",
        "expert",
        name="proficiency_level",
        create_type=False,
    )
    review_status_type = postgresql.ENUM(
        "pending",
        "in_review",
        "approved",
        "rejected",
        name="review_status",
        create_type=False,
    )

    op.create_table(
        "candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("email_hash", sa.String(length=64), nullable=True),
        sa.Column("full_name", sa.String(length=150), nullable=True),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("ssn", sa.String(length=50), nullable=True),
        sa.Column("location", sa.String(length=150), nullable=True),
        sa.Column("linkedin_url", sa.String(length=500), nullable=True),
        sa.Column("github_url", sa.String(length=500), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("years_experience", sa.Float(), nullable=True),
        sa.Column("current_title", sa.String(length=200), nullable=True),
        sa.Column("current_company", sa.String(length=200), nullable=True),
        sa.Column("consent_given", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("consent_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", sa.String(length=100), nullable=False, server_default="default"),
        sa.Column(
            "review_status",
            review_status_type,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("review_assigned_to", sa.String(length=255), nullable=True),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("review_flagged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_confidence", sa.Float(), nullable=True),
        sa.Column("review_flags", postgresql.JSONB(), nullable=True),
        sa.Column("review_approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_approved_by", sa.String(length=255), nullable=True),
        sa.Column("review_rejected_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_rejected_by", sa.String(length=255), nullable=True),
        sa.Column(
            "status",
            candidate_status_type,
            nullable=False,
            server_default="pending",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_index("ix_candidates_email_hash", "candidates", ["email_hash"])
    op.create_index("ix_candidates_created_at", "candidates", ["created_at"])
    op.create_index("ix_candidates_status", "candidates", ["status"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="recruiter"),
        sa.Column("tenant_id", sa.String(length=100), nullable=False, server_default="default"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "correction_stats",
        sa.Column("field_name", sa.String(length=200), primary_key=True, nullable=False),
        sa.Column("correction_count", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "correction_patterns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("field_name", sa.String(length=200), nullable=False),
        sa.Column("original_value", sa.Text(), nullable=False),
        sa.Column("corrected_value", sa.Text(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "last_seen_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_correction_patterns_field_name",
        "correction_patterns",
        ["field_name"],
    )

    op.create_table(
        "corrections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("field_name", sa.String(length=200), nullable=False),
        sa.Column("original_value", sa.Text(), nullable=True),
        sa.Column("corrected_value", sa.Text(), nullable=True),
        sa.Column("corrected_by", sa.String(length=255), nullable=True),
        sa.Column(
            "corrected_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_corrections_candidate_id", "corrections", ["candidate_id"])
    op.create_index("ix_corrections_field_name", "corrections", ["field_name"])

    op.create_table(
        "skill_suggestions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("skill_name", sa.String(length=200), nullable=False),
        sa.Column("normalized_name", sa.String(length=200), nullable=False),
        sa.Column("source", sa.String(length=200), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_skill_suggestions_normalized_name",
        "skill_suggestions",
        ["normalized_name"],
    )
    op.create_index(
        "ix_skill_suggestions_skill_name",
        "skill_suggestions",
        ["skill_name"],
    )

    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("key_hash", sa.String(length=64), nullable=False, unique=True),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="viewer"),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_api_keys_key_hash", "api_keys", ["key_hash"], unique=True)

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", sa.String(length=255), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", sa.String(length=255), nullable=True),
        sa.Column("ip_address", sa.String(length=64), nullable=True),
        sa.Column("details", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )

    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False, unique=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("normalized_name", sa.String(length=150), nullable=True),
    )
    op.create_index("ix_skills_normalized_name", "skills", ["normalized_name"])

    op.create_table(
        "work_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("company_name", sa.String(length=200), nullable=True),
        sa.Column("job_title", sa.String(length=200), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_work_history_candidate_id", "work_history", ["candidate_id"]
    )

    op.create_table(
        "education",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("institution", sa.String(length=255), nullable=True),
        sa.Column("degree", sa.String(length=200), nullable=True),
        sa.Column("field_of_study", sa.String(length=200), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("gpa", sa.Float(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.create_index("ix_education_candidate_id", "education", ["candidate_id"])

    op.create_table(
        "candidate_skills",
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidates.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "skill_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("skills.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("proficiency_level", proficiency_level_type, nullable=True),
        sa.Column("years_experience", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_candidate_skills_candidate_id",
        "candidate_skills",
        ["candidate_id"],
    )
    op.create_index(
        "ix_candidate_skills_skill_id",
        "candidate_skills",
        ["skill_id"],
    )

    op.create_table(
        "parsing_jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column(
            "status",
            parsing_job_status_type,
            nullable=False,
            server_default="pending",
        ),
        sa.Column("task_id", sa.String(length=255), nullable=True),
        sa.Column("last_stage", sa.String(length=100), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("parsed_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("ocr_confidence", sa.Float(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_parsing_jobs_candidate_id", "parsing_jobs", ["candidate_id"]
    )
    op.create_index("ix_parsing_jobs_task_id", "parsing_jobs", ["task_id"])

    op.create_table(
        "revoked_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("jti", sa.String(length=64), nullable=False, unique=True),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "revoked_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_revoked_tokens_jti", "revoked_tokens", ["jti"], unique=True)

    op.create_table(
        "certifications",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column(
            "candidate_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("candidates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("issuing_organization", sa.String(length=200), nullable=True),
        sa.Column("issue_date", sa.Date(), nullable=True),
        sa.Column("expiry_date", sa.Date(), nullable=True),
        sa.Column("credential_id", sa.String(length=100), nullable=True),
    )
    op.create_index(
        "ix_certifications_candidate_id", "certifications", ["candidate_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_certifications_candidate_id", table_name="certifications")
    op.drop_table("certifications")

    op.drop_index("ix_parsing_jobs_task_id", table_name="parsing_jobs")
    op.drop_index("ix_parsing_jobs_candidate_id", table_name="parsing_jobs")
    op.drop_table("parsing_jobs")

    op.drop_index("ix_revoked_tokens_jti", table_name="revoked_tokens")
    op.drop_table("revoked_tokens")

    op.drop_index("ix_skill_suggestions_skill_name", table_name="skill_suggestions")
    op.drop_index("ix_skill_suggestions_normalized_name", table_name="skill_suggestions")
    op.drop_table("skill_suggestions")

    op.drop_index("ix_corrections_field_name", table_name="corrections")
    op.drop_index("ix_corrections_candidate_id", table_name="corrections")
    op.drop_table("corrections")

    op.drop_index("ix_correction_patterns_field_name", table_name="correction_patterns")
    op.drop_table("correction_patterns")

    op.drop_table("correction_stats")

    op.drop_index("ix_api_keys_key_hash", table_name="api_keys")
    op.drop_table("api_keys")

    op.drop_table("audit_logs")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_candidate_skills_skill_id", table_name="candidate_skills")
    op.drop_index("ix_candidate_skills_candidate_id", table_name="candidate_skills")
    op.drop_table("candidate_skills")

    op.drop_index("ix_education_candidate_id", table_name="education")
    op.drop_table("education")

    op.drop_index("ix_work_history_candidate_id", table_name="work_history")
    op.drop_table("work_history")

    op.drop_index("ix_skills_normalized_name", table_name="skills")
    op.drop_table("skills")

    op.drop_index("ix_candidates_status", table_name="candidates")
    op.drop_index("ix_candidates_created_at", table_name="candidates")
    op.drop_index("ix_candidates_email_hash", table_name="candidates")
    op.drop_table("candidates")

    bind = op.get_bind()
    sa.Enum(name="proficiency_level").drop(bind, checkfirst=True)
    sa.Enum(name="parsing_job_status").drop(bind, checkfirst=True)
    sa.Enum(name="candidate_status").drop(bind, checkfirst=True)
    sa.Enum(name="review_status").drop(bind, checkfirst=True)
