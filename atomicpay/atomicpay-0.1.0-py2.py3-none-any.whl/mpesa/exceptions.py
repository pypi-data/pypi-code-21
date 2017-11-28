class MpesaException(Exception):
    """Mpesa Error"""


class AuthTypeError(MpesaException):
    """Authentication Credention Type Error"""


class MpesaCredentialError(MpesaException):
    """Authentication Credention Error"""


class MpesaAuthFailed(MpesaException):
    """Authentication Failed"""


