"""Add new resume tables

Revision ID: add_complete_resume_tables
Revises: 
Create Date: 2024-03-14 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_complete_resume_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    """Add new tables for complete resume JSON format"""
    
    # Create projects table
    op.create_table('projects',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], name='fk_projects_candidate_id')
    )
    
    # Create publications table
    op.create_table('publications',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('publisher', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], name='fk_publications_candidate_id')
    )
    
    # Create volunteer_experience table
    op.create_table('volunteer_experience',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('organization', sa.String(length=500), nullable=False),
        sa.Column('role', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('location', sa.String(length=500), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], name='fk_volunteer_experience_candidate_id')
    )
    
    # Create awards table
    op.create_table('awards',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('issuer', sa.String(length=500), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('award_date', sa.Date(), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], name='fk_awards_candidate_id')
    )
    
    # Create additional_texts table
    op.create_table('additional_texts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('section_type', sa.String(length=100), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], name='fk_additional_texts_candidate_id')
    )
    
    # Create references table
    op.create_table('references',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=sa.text('gen_random_uuid()'), primary_key=True),
        sa.Column('candidate_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=500), nullable=False),
        sa.Column('company', sa.String(length=500), nullable=True),
        sa.Column('position', sa.String(length=500), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('phone', sa.String(length=100), nullable=True),
        sa.Column('relationship', sa.String(length=200), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=True, default=0),
        sa.ForeignKeyConstraint(['candidate_id'], ['candidates.id'], name='fk_references_candidate_id')
    )
    
    # Add new columns to candidates table
    op.add_column('candidates', 'first_name', sa.String(length=200), nullable=True)
    op.add_column('candidates', 'last_name', sa.String(length=200), nullable=True)
    op.add_column('candidates', 'title_before_name', sa.String(length=100), nullable=True)
    op.add_column('candidates', 'title_after_name', sa.String(length=100), nullable=True)
    op.add_column('candidates', 'date_of_birth', sa.Date(), nullable=True)
    op.add_column('candidates', 'street', sa.String(length=500), nullable=True)
    op.add_column('candidates', 'city', sa.String(length=200), nullable=True)
    op.add_column('candidates', 'country', sa.String(length=200), nullable=True)
    op.add_column('candidates', 'postal', sa.String(length=50), nullable=True)
    op.add_column('candidates', 'web', postgresql.JSONB(), nullable=True)
    op.add_column('candidates', 'profile', sa.Text(), nullable=True)
    op.add_column('candidates', 'hobbies', postgresql.JSONB(), nullable=True)
    
    # Create indexes
    op.create_index('idx_projects_candidate_id', 'projects', ['candidate_id'])
    op.create_index('idx_publications_candidate_id', 'publications', ['candidate_id'])
    op.create_index('idx_volunteer_experience_candidate_id', 'volunteer_experience', ['candidate_id'])
    op.create_index('idx_awards_candidate_id', 'awards', ['candidate_id'])
    op.create_index('idx_additional_texts_candidate_id', 'additional_texts', ['candidate_id'])
    op.create_index('idx_references_candidate_id', 'references', ['candidate_id'])


def downgrade() -> None:
    """Remove new tables for complete resume JSON format"""
    
    # Drop indexes
    op.drop_index('idx_projects_candidate_id', table_name='projects')
    op.drop_index('idx_publications_candidate_id', table_name='publications')
    op.drop_index('idx_volunteer_experience_candidate_id', table_name='volunteer_experience')
    op.drop_index('idx_awards_candidate_id', table_name='awards')
    op.drop_index('idx_additional_texts_candidate_id', table_name='additional_texts')
    op.drop_index('idx_references_candidate_id', table_name='references')
    
    # Drop tables
    op.drop_table('references')
    op.drop_table('additional_texts')
    op.drop_table('awards')
    op.drop_table('volunteer_experience')
    op.drop_table('publications')
    op.drop_table('projects')
    
    # Remove columns from candidates table
    op.drop_column('candidates', 'hobbies')
    op.drop_column('candidates', 'profile')
    op.drop_column('candidates', 'web')
    op.drop_column('candidates', 'postal')
    op.drop_column('candidates', 'country')
    op.drop_column('candidates', 'city')
    op.drop_column('candidates', 'street')
    op.drop_column('candidates', 'date_of_birth')
    op.drop_column('candidates', 'title_after_name')
    op.drop_column('candidates', 'title_before_name')
    op.drop_column('candidates', 'last_name')
    op.drop_column('candidates', 'first_name')
