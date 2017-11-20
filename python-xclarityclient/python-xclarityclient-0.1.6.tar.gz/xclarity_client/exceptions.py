import sys
import six


class XClarityClientException(Exception):
    """Base XClarity Client Exception

    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.
    """
    msg_fmt = "An exception occurred."
    code = 500

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if message is None:
            try:
                message = self.msg_fmt % kwargs
            except Exception:
                exc_info = sys.exc_info()
                six.reraise(*exc_info)

        self.message = message
        super(XClarityClientException, self).__init__(message)

    def get_message(self):
        return self.message

    def get_code(self):
        return self.code


class ConnectionFailureException(XClarityClientException):
    msg_fmt = 'Connection Error or Timeout for node %(node_id)s: %(detail)s'


class NodeDetailsException(XClarityClientException):
    msg_fmt = 'Failed to get the details of node %(node_id)s: %(detail)s'


class BadPowerStatusSettingException(XClarityClientException):
    msg_fmt = 'Bad PowerStatus setting: %(action)s'
    code = 400


class FailToSetPowerStatusException(XClarityClientException):
    msg_fmt = 'Failed to set the power status of node %(node_id)s: %(action)s'


class FailToSetBootInfoException(XClarityClientException):
    msg_fmt = 'Failed to set boot info for node %(node_id)s.'


class FailToGetBootOrderException(XClarityClientException):
    msg_fmt = 'Failed to get boot order info for node %(node_id)s. ' \
              'Perhaps this node is not registered to the configured ' \
              'XClarity server.'


# class UnsupportedMachineType(XClarityClientException):
#     msg_fmt = 'Such machine type "%(machine_type)s" is not supported by XClarity Driver. '


class FailToGetAllJobs(XClarityClientException):
    msg_fmt = 'Fail to get all the jobs from XClarity server. ' \
              'status_code is %(status_code)s. '
