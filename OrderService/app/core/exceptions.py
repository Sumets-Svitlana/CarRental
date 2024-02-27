class BaseServiceError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class OrderGettingError(BaseServiceError):
    pass


class OrderCreationError(BaseServiceError):
    pass


class OrderUpdateError(BaseServiceError):
    pass


class OrderDeletingError(BaseServiceError):
    pass


class InternalRequestError(BaseServiceError):
    pass
