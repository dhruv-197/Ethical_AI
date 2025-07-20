"""Add analysis cache table

Revision ID: add_analysis_cache_table
Revises: e7851ccdd41f
Create Date: 2025-07-20 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'add_analysis_cache_table'
down_revision = 'e7851ccdd41f'
branch_labels = None
depends_on = None

def upgrade():
    # Create analysis_cache table
    op.create_table('analysis_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('user_profile', sa.Text(), nullable=True),
        sa.Column('tweets_data', sa.Text(), nullable=True),
        sa.Column('analysis_results', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('is_dynamic', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on username for faster lookups
    op.create_index(op.f('ix_analysis_cache_username'), 'analysis_cache', ['username'], unique=False)

def downgrade():
    # Drop the table
    op.drop_index(op.f('ix_analysis_cache_username'), table_name='analysis_cache')
    op.drop_table('analysis_cache') 