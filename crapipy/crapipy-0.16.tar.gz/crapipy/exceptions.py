"""
Wrapper exceptions
"""


class APIError(Exception):
    pass


class APITimeoutError(APIError):
    pass


class APIClientResponseError(APIError):
    pass
