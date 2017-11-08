class ATPException(Exception):
    pass


class RetryException(ATPException):
    pass


class MaxRetriesExceedException(ATPException):
    pass


__all__ = ['ATPException', 'RetryException', 'MaxRetriesExceedException']
