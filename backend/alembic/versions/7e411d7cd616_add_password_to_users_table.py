"""Add password to users table

Revision ID: 7e411d7cd616
Revises: 2eb9c1e38a1d
Create Date: YYYY-MM-DD HH:MM:SS.SSSSSS

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7e411d7cd616'
down_revision = '2eb9c1e38a1d'
branch_labels = None
depends_on = None


def upgrade():
    # Skip - password column was never added in the first place
    pass


def downgrade():
    # Skip
    pass