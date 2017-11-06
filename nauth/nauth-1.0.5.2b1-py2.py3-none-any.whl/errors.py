class RefreshTokenExpiredError(Exception):
    pass


class UaaLoginError(Exception):
    pass


class UaaAuthorizationError(Exception):
    pass


class AccessTokenRefreshError(Exception):
    pass


class UserAlreadyExistsException(Exception):
    pass


class OldNewPasswordSameException(Exception):
    pass


class UserNotFoundException(Exception):
    pass
