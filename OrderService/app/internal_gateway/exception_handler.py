import json
from typing import Callable

from httpx import HTTPStatusError, RequestError

from app.core.exceptions import InternalRequestError


class InternalGatewayErrorHandler:
    def __call__(self, function: Callable):
        async def wrapper(*args, **kwargs):
            try:
                return await function(*args, **kwargs)
            except (RequestError, HTTPStatusError, json.JSONDecodeError) as err:
                raise InternalRequestError(status_code=500, message=f'Error internal service request; error: {err}')

        return wrapper
