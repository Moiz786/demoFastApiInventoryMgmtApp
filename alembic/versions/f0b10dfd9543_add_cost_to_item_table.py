"""add cost to item table

Revision ID: f0b10dfd9543
Revises: 41d67d42fbb5
Create Date: 2023-04-27 13:20:13.972696

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f0b10dfd9543'
down_revision = '41d67d42fbb5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("items", sa.Column("cost", sa.Float, server_default="0"))


def downgrade() -> None:
    pass
