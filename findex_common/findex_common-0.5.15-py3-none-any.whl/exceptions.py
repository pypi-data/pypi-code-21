import logging


class _BaseException(Exception):
    def __init__(self, message, log_error=True):
        super(_BaseException, self).__init__(message)
        self.message = message
        if log_error:
            logging.error(message)


class ConfigError(_BaseException):
    def __init__(self, message, errors=None):
        super(ConfigError, self).__init__(message)

        self.errors = errors
        logging.error(message)


class SecurityException(_BaseException):
    def __init__(self, message, errors=None):
        super(SecurityException, self).__init__(message)

        self.errors = errors
        logging.error(message)


class ConfigNotFoundError(_BaseException):
    def __init__(self, message, errors=None):
        super(ConfigNotFoundError, self).__init__(message)

        self.errors = errors
        logging.error(message)


class DatabaseException(_BaseException):
    def __init__(self, message, log_error=True):
        super(DatabaseException, self).__init__(message, log_error)


class ElasticSearchException(_BaseException):
    def __init__(self, message, log_error=True):
        super(ElasticSearchException, self).__init__(message, log_error)


class BrowseException(_BaseException):
    def __init__(self, message, errors=None):
        super(BrowseException, self).__init__(message)


class SearchException(_BaseException):
    def __init__(self, message, errors=None):
        super(SearchException, self).__init__(message)
        logging.error(message)


class SearchEmptyException(_BaseException):
    def __init__(self, message, errors=None):
        super(SearchEmptyException, self).__init__(message)
        logging.error(message)


class AmqpParseException(_BaseException):
    def __init__(self, message, errors=None):
        super(AmqpParseException, self).__init__(message)


class JsonParseException(_BaseException):
    def __init__(self, message, errors=None):
        super(JsonParseException, self).__init__(message)


class CrawlException(_BaseException):
    def __init__(self, message, errors=None):
        super(CrawlException, self).__init__(message)


class ThemeException(_BaseException):
    def __init__(self, message, errors=None):
        super(ThemeException, self).__init__(message)


class CrawlBotException(_BaseException):
    def __init__(self, message):
        super(CrawlBotException, self).__init__()
        logging.error(message)

        self.message = message


class RoleException(_BaseException):
    def __init__(self, message):
        super(RoleException, self).__init__(message)


class FindexException(_BaseException):
    def __init__(self, message, log_error=True):
        super(FindexException, self).__init__(message, log_error)


class AuthenticationException(_BaseException):
    def __init__(self, message):
        super(AuthenticationException, self).__init__(message)


class RelayException(_BaseException):
    def __init__(self, message):
        super(RelayException, self).__init__(message)


class StartupError(_BaseException):
    def __init__(self, message):
        super(StartupError, self).__init__(message)
