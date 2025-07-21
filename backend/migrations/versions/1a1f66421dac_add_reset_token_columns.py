"""add_reset_token_columns

Revision ID: 1a1f66421dac
Revises: 1088a68388e3
Create Date: 2025-07-21 10:51:57.007192

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1a1f66421dac'
down_revision: Union[str, None] = '1088a68388e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add reset_token and reset_token_expires columns to users table
    op.add_column('users', sa.Column('reset_token', sa.String(), nullable=True))
    op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove reset_token and reset_token_expires columns from users table
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token')
