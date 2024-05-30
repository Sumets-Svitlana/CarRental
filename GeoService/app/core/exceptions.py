class BaseServiceError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class NotFoundError(BaseServiceError):
    pass


class AlreadyExistsError(BaseServiceError):
    pass
