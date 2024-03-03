import logging
from typing import Any, Callable

from boto3.exceptions import Boto3Error
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class Boto3ErrorHandler:
    def __init__(self, return_value: Any = None):
        self.return_value = return_value

    def __call__(self, function: Callable):
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except (ClientError, Boto3Error) as e:
                logger.error(str(e))
                return self.return_value

        return wrapper
