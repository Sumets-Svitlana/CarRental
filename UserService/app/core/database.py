from asyncio import gather
from pathlib import Path

import yaml

from app.api.schemas.tables import UserTableSchema
from app.storage.dynamodb import get_dynamodb

BASE_DIR = Path(__file__).parent.parent
TABLES_PATH = BASE_DIR / 'models.yaml'


async def migrate_db():
    with open(TABLES_PATH) as file:
        tables = yaml.safe_load(file)

    tasks = (_create_tables(table_name, table_schema) for table_name, table_schema in tables.items())
    await gather(*tasks)


async def _create_tables(table_name: str, table_schema: dict):
    await get_dynamodb().create_tables(table_name, UserTableSchema(**table_schema))
