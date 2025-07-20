"""Add file_hash and transaction_date columns

Revision ID: 4b344657af70
Revises: c9dd9e7861e7
Create Date: 2025-07-07 02:09:37.572958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b344657af70'
down_revision: Union[str, Sequence[str], None] = 'c9dd9e7861e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('transactions', sa.Column('file_hash', sa.String(length=32), nullable=True))
    op.add_column('transactions', sa.Column('transaction_date', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('transactions', 'transaction_date')
