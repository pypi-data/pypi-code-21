# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import abc

from azureml.api.exceptions.ApiException import ApiException


# This class allows us to group all server side errors (5xx error codes) to one hierarchy
class ServerSideException(ApiException):
    __metaclass__ = abc.ABCMeta

    @property
    def status_code(self):
        pass

    def __init__(self, message):
        super(ServerSideException, self).__init__(message)
