from pydantic import BaseModel


class TableSchema(BaseModel):
    AttributeDefinitions: list[dict[str, str]]
    KeySchema: list[dict[str, str]]
    ProvisionedThroughput: dict[str, int]
    GlobalSecondaryIndexes: list[dict]


class UserTableSchema(TableSchema):
    pass
