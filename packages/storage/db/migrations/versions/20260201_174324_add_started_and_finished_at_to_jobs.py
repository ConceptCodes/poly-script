"""add_started_and_finished_at_to_jobs

Revision ID: 20260201_174324
Revises: b1c2d3e4f5g6
Create Date: 2026-02-01 17:43:24.026524

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260201_174324"
down_revision: str | Sequence[str] | None = "b1c2d3e4f5g6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "transcription_jobs", sa.Column("started_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "transcription_jobs", sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("transcription_jobs", "finished_at")
    op.drop_column("transcription_jobs", "started_at")
