from alembic import op
import sqlalchemy as sa

revision = 'add_summary_manually_edited'
down_revision = "004_candidate_achievements"  # ⚠️ must not be None
branch_labels = None
depends_on = None

def upgrade():
    op.add_column(
        'candidates',
        sa.Column(
            'summary_manually_edited',
            sa.Boolean(),
            nullable=False,
            server_default='false'
        )
    )

def downgrade():
    op.drop_column('candidates', 'summary_manually_edited')