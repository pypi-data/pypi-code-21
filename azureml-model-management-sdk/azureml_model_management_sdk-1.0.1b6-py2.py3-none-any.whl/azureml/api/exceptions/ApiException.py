# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import abc


class ApiException(Exception):
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def status_code(self):
        pass

    @property
    def message(self):
        return self._message

    def __init__(self, message):
        Exception.__init__(self)
        self._message = message

    def to_dict(self):
        return {"errorCode": self.status_code, "message": self.message}
