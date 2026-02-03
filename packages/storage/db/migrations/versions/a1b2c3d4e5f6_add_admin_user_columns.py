"""add_admin_user_columns

Revision ID: a1b2c3d4e5f6
Revises: 3d7de3b9fb91
Create Date: 2026-02-01 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "3d7de3b9fb91"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema - add is_suspended and role columns to admin_users."""
    # Add is_suspended column with default False
    op.add_column(
        "admin_users",
        sa.Column("is_suspended", sa.Boolean(), nullable=False, server_default=sa.false()),
    )

    # Add role column with default 'ADMIN'
    op.add_column(
        "admin_users",
        sa.Column("role", sa.String(length=50), nullable=False, server_default="ADMIN"),
    )

    # Add last_login_at column (nullable, as per app-spec)
    op.add_column(
        "admin_users", sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema - remove is_suspended, role, and last_login_at columns from admin_users."""
    # Drop columns in reverse order (last_login_at first, then role, then is_suspended)
    op.drop_column("admin_users", "last_login_at")
    op.drop_column("admin_users", "role")
    op.drop_column("admin_users", "is_suspended")
