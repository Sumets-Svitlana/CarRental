from functools import lru_cache, reduce
from operator import and_
from typing import Protocol

import boto3
from boto3.dynamodb.conditions import Key
from mypy_boto3_dynamodb import DynamoDBClient
from mypy_boto3_dynamodb.service_resource import Table

from app.api.schemas.tables import UserTableSchema
from app.core.config import settings
from app.storage.async_runner import run_async
from app.storage.exception_handler import Boto3ErrorHandler


class BaseRepository(Protocol):
    def create_tables(self, table_name: str, table_schema: UserTableSchema):
        ...

    def query(
        self,
        table_name: str,
        index_name: str | None = None,
        key_condition: dict | None = None,
        projection_expression: str | None = None,
    ) -> list:
        ...

    def update_item(self, table_name: str, key: dict, payload: dict) -> bool:
        ...

    def put_item(self, table_name: str, item: dict) -> bool:
        ...

    def delete_item(self, table_name: str, key: dict) -> bool:
        ...


class DynamodbRepository(BaseRepository):
    def __init__(self, endpoint_url: str | None = None):
        self.__endpoint_url = endpoint_url

    @property
    def __client(self) -> DynamoDBClient:
        return boto3.resource('dynamodb', endpoint_url=self.__endpoint_url)

    @lru_cache
    def __table(self, table_name: str) -> Table:
        return self.__client.Table(table_name)

    @run_async
    @Boto3ErrorHandler()
    def create_tables(self, table_name: str, table_schema: UserTableSchema):
        existing_tables = self.__client.tables.all()
        if table_name not in {table.name for table in existing_tables}:
            self.__client.create_table(TableName=table_name, **table_schema.model_dump())

    @run_async
    @Boto3ErrorHandler(return_value=[])
    def query(
        self,
        table_name: str,
        index_name: str | None = None,
        key_condition: dict | None = None,
        projection_expression: str | None = None,
    ) -> list:
        query_params = {}

        if index_name:
            query_params['IndexName'] = index_name
        if key_condition:
            conditionals = (Key(str(k)).eq(v) for k, v in key_condition.items())
            key_condition_expression = reduce(and_, conditionals)
            query_params['KeyConditionExpression'] = key_condition_expression
        if projection_expression:
            query_params['ProjectionExpression'] = projection_expression

        response = self.__table(table_name).query(**query_params)
        return response.get('Items', [])

    @run_async
    @Boto3ErrorHandler(return_value=False)
    def update_item(self, table_name: str, key: dict, payload: dict) -> bool:
        update_expression, attribute_values = self._generate_conditions_for_update(payload)
        query_params = {
            'Key': key,
            'UpdateExpression': f'set {", ".join(update_expression)}',
            'ExpressionAttributeValues': attribute_values,
            'ReturnValues': 'UPDATED_NEW',
        }
        self.__table(table_name).update_item(**query_params)
        return True

    @staticmethod
    def _generate_conditions_for_update(payload: dict) -> tuple[list, dict]:
        update_expression = []
        attribute_values = {}

        for key, value in payload.items():
            update_expression.append(f'{key}=:{key}')
            attribute_values[f':{key}'] = value

        return update_expression, attribute_values

    @run_async
    @Boto3ErrorHandler(return_value=False)
    def put_item(self, table_name: str, item: dict) -> bool:
        self.__table(table_name).put_item(Item=item)
        return True

    @run_async
    @Boto3ErrorHandler(return_value=False)
    def delete_item(self, table_name: str, key: dict) -> bool:
        self.__table(table_name).delete_item(Key=key)
        return True


@lru_cache
def get_dynamodb() -> DynamodbRepository:
    return DynamodbRepository(
        endpoint_url=settings.AWS_DYNAMODB_ENDPOINT_URL,
    )
