

class EmissionException(Exception):
    """
    Basic exception for errors raised by EmissionRpc
    """


class EmissionBadParameter(EmissionException):
    """
    Options does not exists
    """
    pass


class EmissionLibError(Exception):
    """
    Generic exception for wrapping others exceptions from any library
    """
    def __init__(self, msg, original_exception):
        super(EmissionLibError, self).__init__("{0}: {1}".format(msg, original_exception))
        self.original_exception = original_exception
