"""add timestamps to documents

Revision ID: 9ad9f0f3e54a
Revises: 92bba4d727e5
Create Date: 2026-01-16
"""
from alembic import op
import sqlalchemy as sa

revision = '9ad9f0f3e54a'
down_revision = '92bba4d727e5'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('documents', 
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()'))
    )
    op.add_column('documents', 
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()'))
    )

def downgrade():
    op.drop_column('documents', 'updated_at')
    op.drop_column('documents', 'created_at')
