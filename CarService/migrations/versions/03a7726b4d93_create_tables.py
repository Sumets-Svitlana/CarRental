from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = '03a7726b4d93'
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
                'TOYOTA', 'HONDA', 'FORD', 'BMW', 'MERCEDES_BENZ', 'VOLKSWAGEN', 'NISSAN', 'HYUNDAI', 'AUDI', 'SUBARU',
                'KIA', 'TESLA', 'MAZDA', name='brand'
                ), nullable=False
            ),
        sa.Column('description', sa.String(length=256), nullable=True),
        sa.Column(
            'transmission', sa.Enum('MANUAL', 'AUTOMATIC', 'AUTOMATED_MANUAL', 'HYDROSTATIC', name='transmission'),
            nullable=False
            ),
        sa.Column(
            'fuel_type', sa.Enum('GASOLINE', 'DIESEL', 'ELECTRIC', 'HYBRID', 'NATURAL_GAS', 'ETHANOL', name='fueltype'),
            nullable=False
            ),
        sa.Column(
            'color', sa.Enum('WHITE', 'BLACK', 'SILVER', 'GRAY', 'BLUE', 'BROWN', 'GOLD', 'BRONZE', name='color'),
            nullable=False
            ),
        sa.Column(
            'category', sa.Enum(
                'ECONOMY', 'COMPACT', 'SUV', 'CROSSOVER', 'LUXURY', 'SPORTS', 'CONVERTIBLE', 'MINIVAN', 'PICKUP_TRUCK',
                name='category'
                ), nullable=False
            ),
        sa.Column('engine_capacity', sa.Float(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('ORDERED', 'REPAIRED', 'FREE', name='carstatuse'), nullable=False),
        sa.Column('station_id', sa.UUID(), nullable=False),
        sa.Column('cost_per_hour', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('image'),
        sa.UniqueConstraint('number')
        )


def downgrade() -> None:
    op.drop_table('cars')
