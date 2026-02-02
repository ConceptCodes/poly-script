from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '4a8c9d2e5f61'
down_revision = '3d7de3b9fb91'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('admin_users', sa.Column('is_suspended', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('admin_users', sa.Column('role', sa.String(length=50), nullable=False, server_default='ADMIN'))


def downgrade():
    op.drop_column('admin_users', 'role')
    op.drop_column('admin_users', 'is_suspended')
