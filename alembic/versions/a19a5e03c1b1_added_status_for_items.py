"""added status for items

Revision ID: a19a5e03c1b1
Revises: 8f7a8ba932c5
Create Date: 2023-04-26 17:48:58.796957

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a19a5e03c1b1'
down_revision = '8f7a8ba932c5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("items", sa.Column("status", sa.String, server_default="available"))


def downgrade() -> None:
    pass
