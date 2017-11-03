
class RunTheShowException(Exception):
    """
    Basic exception raised by RunTheShow
    """


class RunTheShowBadParamater(RunTheShowException):
    """
    Options does not exists
    """
    pass


class EpisodeNotFound(RunTheShowException):
    """
    Raised when episode not found
    """


class SeasonNotFound(RunTheShowException):
    """
    Raised whe season not found
    """


class RunTheShowLibError(Exception):
    """
    Generic exception for wrapping others exceptions from any library
    """
    def __init__(self, msg, original_exception):
        super(RunTheShowLibError, self).__init__("{0}: {1}".format(msg, original_exception))
        self.original_exception = original_exception

