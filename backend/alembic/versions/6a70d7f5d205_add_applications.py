"""add applications

Revision ID: 6a70d7f5d205
Revises: a75325633900
Create Date: 2026-08-03 03:49:37.957212

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '6a70d7f5d205'
down_revision: Union[str, Sequence[str], None] = 'a75325633900'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('applications',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('opportunity_id', sa.UUID(), nullable=False),
    sa.Column('student_id', sa.UUID(), nullable=False),
    sa.Column('status', sa.Enum('submitted', 'under_review', 'shortlisted', 'accepted', 'rejected', 'withdrawn', name='application_status'), nullable=False),
    sa.Column('cover_letter', sa.Text(), nullable=True),
    sa.Column('resume_path', sa.String(length=500), nullable=True),
    sa.Column('profile_snapshot', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    sa.Column('employer_note', sa.Text(), nullable=True),
    sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['opportunity_id'], ['opportunities.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['student_id'], ['users.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('opportunity_id', 'student_id', name='uq_application_opportunity_student')
    )
    op.create_index('ix_applications_created_at', 'applications', ['created_at'], unique=False)
    op.create_index('ix_applications_opportunity_id', 'applications', ['opportunity_id'], unique=False)
    op.create_index('ix_applications_status', 'applications', ['status'], unique=False)
    op.create_index('ix_applications_student_id', 'applications', ['student_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_applications_student_id', table_name='applications')
    op.drop_index('ix_applications_status', table_name='applications')
    op.drop_index('ix_applications_opportunity_id', table_name='applications')
    op.drop_index('ix_applications_created_at', table_name='applications')
    op.drop_table('applications')
