from __future__ import absolute_import, division, print_function


class KillOnFailureError(Exception):
    def __init__(self, message=None, **kwargs):
        self.info = message
        super(KillOnFailureError, self).__init__(message, **kwargs)
