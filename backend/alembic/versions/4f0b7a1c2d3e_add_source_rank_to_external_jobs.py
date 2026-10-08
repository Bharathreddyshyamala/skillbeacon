"""add source rank to external jobs

Revision ID: 4f0b7a1c2d3e
Revises: 81cad4f56b50
Create Date: 2026-08-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4f0b7a1c2d3e"
down_revision: Union[
    str,
    Sequence[str],
    None,
] = "81cad4f56b50"
branch_labels: Union[
    str,
    Sequence[str],
    None,
] = None
depends_on: Union[
    str,
    Sequence[str],
    None,
] = None


def upgrade() -> None:
    op.add_column(
        "external_jobs",
        sa.Column(
            "source_rank",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_external_jobs_source_rank",
        "external_jobs",
        [
            "source_id",
            "source_rank",
        ],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_external_jobs_source_rank",
        table_name="external_jobs",
    )

    op.drop_column(
        "external_jobs",
        "source_rank",
    )
