"""Create_tables

Revision ID: b6f084f6ccac
Revises: 
Create Date: 2024-05-30 15:06:23.096202

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'b6f084f6ccac'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'cars',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(length=16), nullable=False),
        sa.Column('image', sa.String(length=256), nullable=True),
        sa.Column(
            'brand', sa.Enum(
                'toyota', 'honda', 'ford', 'bmw', 'mercedes_benz', 'volkswagen', 'nissan', 'hyundai', 'audi', 'subaru',
                'kia', 'tesla', 'mazda', name='brand'
            ), nullable=False
        ),
        sa.Column('description', sa.String(length=256), nullable=True),
        sa.Column(
            'transmission', sa.Enum('manual', 'automatic', 'automated_manual', 'hydrostatic', name='transmission'),
            nullable=False
        ),
        sa.Column(
            'fuel_type', sa.Enum('gasoline', 'diesel', 'electric', 'hybrid', 'natural_gas', 'ethanol', name='fueltype'),
            nullable=False
        ),
        sa.Column(
            'color', sa.Enum('white', 'black', 'silver', 'gray', 'blue', 'brown', 'gold', 'bronze', name='color'),
            nullable=False
        ),
        sa.Column(
            'category', sa.Enum(
                'economy', 'compact', 'suv', 'crossover', 'luxury', 'sports', 'convertible', 'minivan', 'pickup_truck',
                name='category'
            ), nullable=False
        ),
        sa.Column('engine_capacity', sa.Float(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('ordered', 'repaired', 'free', name='carstatuse'), nullable=False),
        sa.Column('station_id', sa.UUID(), nullable=False),
        sa.Column('cost_per_hour', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('image'),
        sa.UniqueConstraint('number')
    )


def downgrade() -> None:
    op.drop_table('cars')
