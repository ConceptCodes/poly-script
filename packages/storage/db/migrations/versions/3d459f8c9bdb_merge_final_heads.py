"""merge_final_heads

Revision ID: 3d459f8c9bdb
Revises: 20260201_174324, 20260201_191007
Create Date: 2026-02-02 16:04:58.769700

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "3d459f8c9bdb"
down_revision: str | Sequence[str] | None = "20260201_191007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
