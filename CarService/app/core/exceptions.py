class BaseServiceError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class CarGettingError(BaseServiceError):
    pass


class CarCreationError(BaseServiceError):
    pass


class CarUpdateError(BaseServiceError):
    pass


class CarDeletingError(BaseServiceError):
    pass


class UploadFileError(BaseServiceError):
    pass


class InternalRequestError(BaseServiceError):
    pass
