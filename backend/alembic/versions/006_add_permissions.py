"""Add permissions and role permissions tables

Revision ID: 006_add_permissions
Revises: 005_add_salary_fields
Create Date: 2026-05-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '006_add_permissions'
down_revision: Union[str, None] = '005_add_salary_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('module', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('name'),
    )
    op.create_index('ix_permissions_name', 'permissions', ['name'])
    op.create_index('ix_permissions_module', 'permissions', ['module'])
    
    # Create role_permissions table
    op.create_table(
        'role_permissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('permission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.UniqueConstraint('role', 'permission_id', name='uq_role_permission'),
    )
    op.create_index('ix_role_permissions_role', 'role_permissions', ['role'])
    op.create_index('ix_role_permissions_permission_id', 'role_permissions', ['permission_id'])
    
    # Insert default permissions
    op.execute("""
        INSERT INTO permissions (name, description, module) VALUES
        ('candidate.view', 'View candidates', 'candidate'),
        ('candidate.create', 'Create candidates', 'candidate'),
        ('candidate.edit', 'Edit candidates', 'candidate'),
        ('candidate.delete', 'Delete candidates', 'candidate'),
        ('job.view', 'View jobs', 'job'),
        ('job.create', 'Create jobs', 'job'),
        ('job.edit', 'Edit jobs', 'job'),
        ('job.delete', 'Delete jobs', 'job'),
        ('matching.view', 'View matching results', 'matching'),
        ('matching.run', 'Run matching', 'matching'),
        ('analytics.view', 'View analytics', 'analytics'),
        ('analytics.export', 'Export analytics', 'analytics'),
        ('labeling.view', 'View labels', 'labeling'),
        ('labeling.edit', 'Edit labels', 'labeling'),
        ('user.view', 'View users', 'user'),
        ('user.create', 'Create users', 'user'),
        ('user.edit', 'Edit users', 'user'),
        ('user.delete', 'Delete users', 'user'),
        ('settings.manage', 'Manage system settings', 'settings')
    """)
    
    # Insert default role permissions for admin (all permissions)
    op.execute("""
        INSERT INTO role_permissions (role, permission_id)
        SELECT 'admin', id FROM permissions
    """)
    
    # Insert default role permissions for recruiter
    op.execute("""
        INSERT INTO role_permissions (role, permission_id)
        SELECT 'recruiter', id FROM permissions 
        WHERE name IN (
            'candidate.view', 'candidate.create', 'candidate.edit', 'candidate.delete',
            'job.view', 'job.create', 'job.edit', 'job.delete',
            'matching.view', 'analytics.view'
        )
    """)
    
    # Insert default role permissions for hr
    op.execute("""
        INSERT INTO role_permissions (role, permission_id)
        SELECT 'hr', id FROM permissions 
        WHERE name IN (
            'candidate.view', 'candidate.edit', 'analytics.view'
        )
    """)
    
    # Insert default role permissions for viewer
    op.execute("""
        INSERT INTO role_permissions (role, permission_id)
        SELECT 'viewer', id FROM permissions 
        WHERE name IN (
            'candidate.view', 'analytics.view'
        )
    """)

def downgrade() -> None:
    op.drop_table('role_permissions')
    op.drop_table('permissions')
