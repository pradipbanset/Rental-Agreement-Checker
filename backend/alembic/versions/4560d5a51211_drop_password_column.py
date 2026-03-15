"""Drop password column

Revision ID: 4560d5a51211
Revises: ae4f1ff84055
Create Date: 2026-01-07 00:56:18.181715

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4560d5a51211'
down_revision: Union[str, Sequence[str], None] = 'ae4f1ff84055'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
