"""change clauses to JSONB in analysis

Revision ID: 92bba4d727e5
Revises: 4d38e0697a16
Create Date: 2026-01-08 15:44:28.309504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '92bba4d727e5'
down_revision: Union[str, Sequence[str], None] = '4d38e0697a16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
