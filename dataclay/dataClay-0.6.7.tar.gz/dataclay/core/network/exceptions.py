from dataclay.core import constants

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'


class RemoteException(RuntimeError):
    """Exception thrown in client code after a RPC call return with an exception."""

    def __init__(self, error_code, error_string):
        self.error_code = error_code
        self.error_string = error_string
        try:
            self.error_name = constants.error_codes.error_codes[error_code]
        except KeyError:
            self.error_name = "UNDEFINED".format(error_code)
        super(RuntimeError, self).__init__("Error [{}: {}]. Server response: {}".format(
            self.error_code, self.error_name, self.error_string))


class NetworkError(RuntimeError):
    """Exception when some socket input/output recv or similar operation
    does not behave as expected."""
    def __init__(self, *args):
        super(RuntimeError, self).__init__(*args)


class ClientError(RuntimeError):
    """Exception when a client has sent some invalid request."""
    def __init__(self, *args):
        super(RuntimeError, self).__init__(*args)
