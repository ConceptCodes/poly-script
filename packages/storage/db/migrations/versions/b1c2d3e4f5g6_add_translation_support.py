from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "b1c2d3e4f5g6"
down_revision: Union[str, Sequence[str], None] = "4a8c9d2e5f61"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add translation tracking to teams and create translation_artifacts table."""
    # Create translation status enum type
    op.execute("CREATE TYPE translationstatus AS ENUM ('PENDING', 'RUNNING', 'SUCCEEDED', 'FAILED', 'CANCELED')")
    
    # Add target_language to transcription_jobs
    op.add_column('transcription_jobs', sa.Column('target_language', sa.String(length=10), nullable=True))
    
    # Add monthly_translation_count to teams
    op.add_column('teams', sa.Column('monthly_translation_count', sa.Integer(), nullable=False, server_default='0'))
    
    # Create translation_artifacts table
    op.create_table(
        'translation_artifacts',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('job_id', sa.Uuid(), nullable=False),
        sa.Column('status', sa.Enum(name='translationstatus', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('target_language', sa.String(length=10), nullable=False),
        sa.Column('text', sa.Text(), nullable=True),
        sa.Column('segments', sa.JSON(), nullable=True),
        sa.Column('engine', sa.String(length=50), nullable=True),
        sa.Column('engine_version', sa.String(length=50), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['transcription_jobs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('job_id')
    )


def downgrade() -> None:
    """Remove translation support."""
    op.drop_table('translation_artifacts')
    op.drop_column('transcription_jobs', 'target_language')
    op.drop_column('teams', 'monthly_translation_count')
    op.execute('DROP TYPE translationstatus')
