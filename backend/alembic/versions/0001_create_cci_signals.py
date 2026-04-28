"""create cci_signals table
Revision ID: 0001_create_cci_signals
Revises: 
Create Date: 2026-04-28 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001_create_cci_signals'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'cci_signals',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('stock_code', sa.String(length=255), nullable=False, index=True),
        sa.Column('stock_name', sa.String(length=255), nullable=True),
        sa.Column('signal_type', sa.String(length=255), nullable=False),
        sa.Column('timeframe', sa.String(length=32), nullable=False),
        sa.Column('signal_date', sa.Date, nullable=False, index=True),
        sa.Column('meta', sa.JSON, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('stock_code', 'timeframe', 'signal_date', name='uix_stock_timeframe_date')
    )


def downgrade():
    op.drop_table('cci_signals')
