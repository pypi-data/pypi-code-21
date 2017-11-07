# coding: utf-8

"""Base exception handling.
"""
from __future__ import absolute_import, print_function, unicode_literals, division

import six
import logging
import webob.exc

_ = (lambda v: v)
LOG = logging.getLogger(__name__)
_exc_map = {}


def _exc_map_f():
    for http in dir(webob.exc):
        if http.startswith("HTTP"):
            cls = getattr(webob.exc, http)
            code = getattr(cls, "code", None)
            if code and issubclass(cls, webob.exc.WSGIHTTPException):
                _exc_map.setdefault(code, [])
                _exc_map[code].append(cls)
_exc_map_f()


def convert_exc(code, first=True, strict=False):
    clss = _exc_map.get(code, None)
    if clss is None:
        if strict:
            return None
        code = int(code // 100) * 100
        clss = _exc_map.get(code)

    if first:
        return clss[0]
    else:
        return clss


class ConvertedException(webob.exc.WSGIHTTPException):
    def __init__(self, code=0, title="", explanation=""):
        self.code = code
        self.title = title
        self.explanation = explanation
        super(ConvertedException, self).__init__()


def _cleanse_dict(original):
    """Strip all admin_password, new_pass, rescue_pass keys from a dict."""
    return {k: v for k, v in six.iteritems(original) if "_pass" not in k}


class ExceptionBase(Exception):
    """Base Nova Exception
    To correctly use this class, inherit from it and define
    a 'msg_fmt' property. That msg_fmt will get printf'd
    with the keyword arguments provided to the constructor.
    """
    msg_fmt = _("An unknown exception occurred.")
    code = 500
    headers = {}
    safe = False

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs

        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass

        if not message:
            try:
                message = self.msg_fmt % kwargs
            except Exception:
                LOG.exception(_('Exception in string format operation'))
                for name, value in six.iteritems(kwargs):
                    LOG.error("%s: %s" % (name, value))    # noqa

                message = self.msg_fmt

        self.message = message
        super(ExceptionBase, self).__init__(message)

    def format_message(self):
        # NOTE(mrodden): use the first argument to the python Exception object
        # which should be our full ExceptionBase message, (see __init__)
        return self.args[0]


class Forbidden(ExceptionBase):
    ec2_code = 'AuthFailure'
    msg_fmt = _("Not authorized.")
    code = 403


class AdminRequired(Forbidden):
    msg_fmt = _("User does not have admin privileges")


class Invalid(ExceptionBase):
    msg_fmt = _("Unacceptable parameters.")
    code = 400


class InvalidAttribute(Invalid):
    msg_fmt = _("Attribute not supported: %(attr)s")


class ServiceUnavailable(Invalid):
    msg_fmt = _("Service is unavailable at this time.")


class InvalidToken(Invalid):
    msg_fmt = _("The token '%(token)s' is invalid or has expired")


class InvalidConnectionInfo(Invalid):
    msg_fmt = _("Invalid Connection Info")


class InvalidHostname(Invalid):
    msg_fmt = _("Invalid characters in hostname '%(hostname)s'")


class InvalidContentType(Invalid):
    msg_fmt = _("Invalid content type %(content_type)s.")


class InvalidAPIVersionString(Invalid):
    msg_fmt = _("API Version String %(version)s is of invalid format. Must "
                "be of format MajorNum.MinorNum.")


class InvalidInput(Invalid):
    msg_fmt = _("Invalid input received: %(reason)s")


class VersionNotFoundForAPIMethod(Invalid):
    msg_fmt = _("API version %(version)s is not supported on this method.")


class BadRequest(ExceptionBase):
    msg_fmt = _("Bad Request")
    code = 400


class MalformedRequestBody(BadRequest):
    msg_fmt = _("Malformed message body: %(reason)s")


class NotFound(ExceptionBase):
    msg_fmt = _("Resource could not be found.")
    code = 404


class FileNotFound(NotFound):
    msg_fmt = _("File %(file_path)s could not be found.")


class ConfigNotFound(ExceptionBase):
    msg_fmt = _("Could not find config at %(path)s")


class PasteAppNotFound(ExceptionBase):
    msg_fmt = _("Could not load paste app '%(name)s' from %(path)s")


class CoreAPIMissing(ExceptionBase):
    msg_fmt = _("Core API extensions are missing: %(missing_apis)s")


# Cannot be templated, msg needs to be constructed when raised.
class InternalError(ExceptionBase):
    ec2_code = 'InternalError'
    msg_fmt = "%(err)s"


class SocketPortInUseException(ExceptionBase):
    msg_fmt = _("Not able to bind %(host)s:%(port)d, %(error)s")
