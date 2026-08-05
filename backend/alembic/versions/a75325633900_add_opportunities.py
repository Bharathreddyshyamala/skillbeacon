"""add opportunities

Revision ID: a75325633900
Revises: 72673a64f3cd
Create Date: 2026-08-02 02:38:11.302972

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a75325633900'
down_revision: Union[str, Sequence[str], None] = '72673a64f3cd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('opportunities',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('employer_id', sa.UUID(), nullable=False),
    sa.Column('company_name', sa.String(length=200), nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('location', sa.String(length=200), nullable=True),
    sa.Column('work_mode', sa.String(length=30), nullable=False),
    sa.Column('opportunity_type', sa.String(length=30), nullable=False),
    sa.Column('employment_type', sa.String(length=30), nullable=True),
    sa.Column('salary_min', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('salary_max', sa.Numeric(precision=12, scale=2), nullable=True),
    sa.Column('currency', sa.String(length=3), nullable=False),
    sa.Column('application_url', sa.String(length=500), nullable=True),
    sa.Column('deadline', sa.Date(), nullable=True),
    sa.Column('status', sa.String(length=30), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['employer_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_opportunities_employer_id'), 'opportunities', ['employer_id'], unique=False)
    op.create_index(op.f('ix_opportunities_status'), 'opportunities', ['status'], unique=False)
    op.create_index(op.f('ix_opportunities_title'), 'opportunities', ['title'], unique=False)
    op.create_table('opportunity_skills',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('opportunity_id', sa.UUID(), nullable=False),
    sa.Column('skill_id', sa.UUID(), nullable=False),
    sa.Column('minimum_level', sa.String(length=30), nullable=False),
    sa.Column('required', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['skill_id'], ['skills.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('opportunity_id', 'skill_id', name='uq_opportunity_skill')
    )
    op.create_index(op.f('ix_opportunity_skills_opportunity_id'), 'opportunity_skills', ['opportunity_id'], unique=False)
    op.create_index(op.f('ix_opportunity_skills_skill_id'), 'opportunity_skills', ['skill_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_opportunity_skills_skill_id'), table_name='opportunity_skills')
    op.drop_index(op.f('ix_opportunity_skills_opportunity_id'), table_name='opportunity_skills')
    op.drop_table('opportunity_skills')
    op.drop_index(op.f('ix_opportunities_title'), table_name='opportunities')
    op.drop_index(op.f('ix_opportunities_status'), table_name='opportunities')
    op.drop_index(op.f('ix_opportunities_employer_id'), table_name='opportunities')
    op.drop_table('opportunities')
