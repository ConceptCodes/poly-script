import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4a8c9d2e5f61"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade():
    # Columns is_suspended and role were already added by a1b2c3d4e5f6
    # This migration is now a no-op - indexes are added by 20260201_191007
    pass


def downgrade():
    pass
