"""add employer challenges

Revision ID: c6cf2d464ed8
Revises: cb0c7ac7b904
Create Date: 2026-08-04 05:14:28.202229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = 'c6cf2d464ed8'
down_revision: Union[str, Sequence[str], None] = 'cb0c7ac7b904'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table('challenges',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('employer_id', sa.UUID(), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('company_name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('instructions', sa.Text(), nullable=False),
    sa.Column('deliverables', sa.Text(), nullable=True),
    sa.Column('challenge_type', sa.Enum('coding', 'data', 'case_study', 'design', 'general', name='challenge_type'), nullable=False),
    sa.Column('difficulty', sa.Enum('beginner', 'intermediate', 'advanced', name='challenge_difficulty'), nullable=False),
    sa.Column('status', sa.Enum('draft', 'open', 'closed', name='challenge_status'), nullable=False),
    sa.Column('deadline', sa.Date(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['employer_id'], ['users.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_challenges_created_at', 'challenges', ['created_at'], unique=False)
    op.create_index('ix_challenges_deadline', 'challenges', ['deadline'], unique=False)
    op.create_index('ix_challenges_employer_id', 'challenges', ['employer_id'], unique=False)
    op.create_index('ix_challenges_status', 'challenges', ['status'], unique=False)
    op.create_index('ix_challenges_type', 'challenges', ['challenge_type'], unique=False)
    op.create_table('challenge_skills',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('challenge_id', sa.UUID(), nullable=False),
    sa.Column('skill_id', sa.UUID(), nullable=False),
    sa.Column('minimum_level', sa.Enum('beginner', 'intermediate', 'advanced', 'expert', name='challenge_skill_level'), nullable=False),
    sa.Column('required', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('challenge_id', 'skill_id', name='uq_challenge_skill_challenge_skill')
    )
    op.create_table('challenge_submissions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('challenge_id', sa.UUID(), nullable=False),
    sa.Column('student_id', sa.UUID(), nullable=False),
    sa.Column('submission_text', sa.Text(), nullable=True),
    sa.Column('repository_url', sa.String(length=500), nullable=True),
    sa.Column('demo_url', sa.String(length=500), nullable=True),
    sa.Column('profile_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('status', sa.Enum('submitted', 'under_review', 'accepted', 'rejected', name='challenge_submission_status'), nullable=False),
    sa.Column('score', sa.Integer(), nullable=True),
    sa.Column('employer_feedback', sa.Text(), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('score IS NULL OR (score >= 0 AND score <= 100)', name='ck_challenge_submission_score'),
    sa.ForeignKeyConstraint(['challenge_id'], ['challenges.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('challenge_id', 'student_id', name='uq_challenge_submission_challenge_student')
    )
    op.create_index('ix_challenge_submissions_challenge_id', 'challenge_submissions', ['challenge_id'], unique=False)
    op.create_index('ix_challenge_submissions_created_at', 'challenge_submissions', ['created_at'], unique=False)
    op.create_index('ix_challenge_submissions_status', 'challenge_submissions', ['status'], unique=False)
    op.create_index('ix_challenge_submissions_student_id', 'challenge_submissions', ['student_id'], unique=False)



def downgrade() -> None:
    """Downgrade schema."""

    op.drop_index('ix_challenge_submissions_student_id', table_name='challenge_submissions')
    op.drop_index('ix_challenge_submissions_status', table_name='challenge_submissions')
    op.drop_index('ix_challenge_submissions_created_at', table_name='challenge_submissions')
    op.drop_index('ix_challenge_submissions_challenge_id', table_name='challenge_submissions')
    op.drop_table('challenge_submissions')
    op.drop_table('challenge_skills')
    op.drop_index('ix_challenges_type', table_name='challenges')
    op.drop_index('ix_challenges_status', table_name='challenges')
    op.drop_index('ix_challenges_employer_id', table_name='challenges')
    op.drop_index('ix_challenges_deadline', table_name='challenges')
    op.drop_index('ix_challenges_created_at', table_name='challenges')
    op.drop_table('challenges')

