"""Add file_hash and timestamp to transactions

Revision ID: de4ed55c9c57
Revises: 7f8749fa3ef0
Create Date: 2025-07-07 01:53:15.395672

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de4ed55c9c57'
down_revision: Union[str, Sequence[str], None] = '7f8749fa3ef0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('transactions', sa.Column('transaction_date', sa.DateTime(), nullable=True))

def downgrade() -> None:
    op.drop_column('transactions', 'transaction_date')



