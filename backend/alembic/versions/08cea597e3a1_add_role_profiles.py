"""add role profiles

Revision ID: 08cea597e3a1
Revises: eb42ba60e8c0
Create Date: 2026-07-30 06:45:22.231800

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '08cea597e3a1'
down_revision: Union[str, Sequence[str], None] = 'eb42ba60e8c0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('employer_profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('company_name', sa.String(length=200), nullable=True),
    sa.Column('industry', sa.String(length=150), nullable=True),
    sa.Column('company_size', sa.String(length=100), nullable=True),
    sa.Column('website', sa.String(length=500), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('location', sa.String(length=250), nullable=True),
    sa.Column('logo_path', sa.String(length=500), nullable=True),
    sa.Column('verification_status', sa.String(length=30), nullable=False),
    sa.Column('is_public', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_employer_profiles_user_id'), 'employer_profiles', ['user_id'], unique=True)
    op.create_table('mentor_profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('display_name', sa.String(length=200), nullable=True),
    sa.Column('headline', sa.String(length=200), nullable=True),
    sa.Column('bio', sa.Text(), nullable=True),
    sa.Column('industry', sa.String(length=150), nullable=True),
    sa.Column('years_of_experience', sa.Integer(), nullable=True),
    sa.Column('languages', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('mentorship_formats', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('availability', sa.Text(), nullable=True),
    sa.Column('is_accepting_requests', sa.Boolean(), nullable=False),
    sa.Column('is_public', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_mentor_profiles_user_id'), 'mentor_profiles', ['user_id'], unique=True)
    op.create_table('student_profiles',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('first_name', sa.String(length=100), nullable=True),
    sa.Column('last_name', sa.String(length=100), nullable=True),
    sa.Column('headline', sa.String(length=200), nullable=True),
    sa.Column('summary', sa.Text(), nullable=True),
    sa.Column('education', sa.Text(), nullable=True),
    sa.Column('work_experience', sa.Text(), nullable=True),
    sa.Column('preferred_roles', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('preferred_locations', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('work_authorization', sa.String(length=100), nullable=True),
    sa.Column('availability', sa.String(length=100), nullable=True),
    sa.Column('career_goals', sa.Text(), nullable=True),
    sa.Column('github_url', sa.String(length=500), nullable=True),
    sa.Column('linkedin_url', sa.String(length=500), nullable=True),
    sa.Column('portfolio_url', sa.String(length=500), nullable=True),
    sa.Column('resume_path', sa.String(length=500), nullable=True),
    sa.Column('is_public', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_profiles_user_id'), 'student_profiles', ['user_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_student_profiles_user_id'), table_name='student_profiles')
    op.drop_table('student_profiles')
    op.drop_index(op.f('ix_mentor_profiles_user_id'), table_name='mentor_profiles')
    op.drop_table('mentor_profiles')
    op.drop_index(op.f('ix_employer_profiles_user_id'), table_name='employer_profiles')
    op.drop_table('employer_profiles')
