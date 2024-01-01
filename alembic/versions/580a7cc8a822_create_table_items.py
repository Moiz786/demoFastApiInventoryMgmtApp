"""create table Items

Revision ID: 580a7cc8a822
Revises: 
Create Date: 2023-04-26 16:21:33.626942

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '580a7cc8a822'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'items',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('description', sa.String, nullable=False),
        sa.Column('price', sa.Float, nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('date', sa.Date, nullable=False),
    )


def downgrade() -> None:
    pass
