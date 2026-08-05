"""add skill passport

Revision ID: 72673a64f3cd
Revises: 08cea597e3a1
Create Date: 2026-08-01 06:26:18.618186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '72673a64f3cd'
down_revision: Union[str, Sequence[str], None] = '08cea597e3a1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('skills',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('category', sa.String(length=120), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skills_category'), 'skills', ['category'], unique=False)
    op.create_index(op.f('ix_skills_name'), 'skills', ['name'], unique=True)
    op.create_table('user_skills',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('skill_id', sa.UUID(), nullable=False),
    sa.Column('level', sa.Enum('beginner', 'intermediate', 'advanced', 'expert', name='skill_level'), nullable=False),
    sa.Column('confidence_score', sa.Float(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.CheckConstraint('confidence_score >= 0 AND confidence_score <= 100', name='ck_user_skill_confidence_score'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id', 'skill_id', name='uq_user_skill')
    )
    op.create_index(op.f('ix_user_skills_skill_id'), 'user_skills', ['skill_id'], unique=False)
    op.create_index(op.f('ix_user_skills_user_id'), 'user_skills', ['user_id'], unique=False)
    op.create_table('skill_evidence',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('user_skill_id', sa.UUID(), nullable=False),
    sa.Column('evidence_type', sa.Enum('github_project', 'certificate', 'assessment', 'employer_challenge', 'work_experience', 'mentor_review', 'other', name='evidence_type'), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('url', sa.String(length=500), nullable=True),
    sa.Column('score', sa.Float(), nullable=True),
    sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='verification_status'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_skill_id'], ['user_skills.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_skill_evidence_user_skill_id'), 'skill_evidence', ['user_skill_id'], unique=False)
    op.create_table('skill_verifications',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('evidence_id', sa.UUID(), nullable=False),
    sa.Column('verifier_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('pending', 'approved', 'rejected', name='skill_verification_status'), nullable=False),
    sa.Column('comments', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['evidence_id'], ['skill_evidence.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['verifier_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('evidence_id', 'verifier_id', name='uq_evidence_verifier')
    )
    op.create_index(op.f('ix_skill_verifications_evidence_id'), 'skill_verifications', ['evidence_id'], unique=False)
    op.create_index(op.f('ix_skill_verifications_verifier_id'), 'skill_verifications', ['verifier_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_skill_verifications_verifier_id'), table_name='skill_verifications')
    op.drop_index(op.f('ix_skill_verifications_evidence_id'), table_name='skill_verifications')
    op.drop_table('skill_verifications')
    op.drop_index(op.f('ix_skill_evidence_user_skill_id'), table_name='skill_evidence')
    op.drop_table('skill_evidence')
    op.drop_index(op.f('ix_user_skills_user_id'), table_name='user_skills')
    op.drop_index(op.f('ix_user_skills_skill_id'), table_name='user_skills')
    op.drop_table('user_skills')
    op.drop_index(op.f('ix_skills_name'), table_name='skills')
    op.drop_index(op.f('ix_skills_category'), table_name='skills')
    op.drop_table('skills')
