from __future__ import unicode_literals
import logging

log = logging.getLogger(__name__)


class AuthError(Exception):
    pass

class UnknownError(Exception):
    pass