"""Create phone_number for user column

Revision ID: 087c2750ff25
Revises: 
Create Date: 2025-01-23 23:52:24.339083

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '087c2750ff25'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # alembic: `op`
    # sqlalchemy: `sa`
    # table name: `users`
    # column name: "phone_number"
    # column type: sa.String(),
    # nullable True
    op.add_column('users', sa.Column("phone_number", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('users', 'phone_number')
