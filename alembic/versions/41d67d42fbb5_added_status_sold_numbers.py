"""added status sold numbers

Revision ID: 41d67d42fbb5
Revises: a19a5e03c1b1
Create Date: 2023-04-26 17:58:19.510290

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41d67d42fbb5'
down_revision = 'a19a5e03c1b1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("items", sa.Column("sold_units", sa.Integer, server_default="0"))


def downgrade() -> None:
    pass
