class BaseServiceError(Exception):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UserGettingError(BaseServiceError):
    pass


class UserCreatingError(BaseServiceError):
    pass


class UserUpdateError(BaseServiceError):
    pass


class UserDeletingError(BaseServiceError):
    pass


class EmailVerificationError(BaseServiceError):
    pass


class UserVerificationError(BaseServiceError):
    pass


class UserLoginError(BaseServiceError):
    pass
