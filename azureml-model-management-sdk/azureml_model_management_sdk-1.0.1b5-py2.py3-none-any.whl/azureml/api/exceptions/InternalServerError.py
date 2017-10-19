# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azureml.api.exceptions.ServerSideException import ServerSideException


class InternalServerException(ServerSideException):
    @property
    def status_code(self):
        return 500

    def __init__(self, message):
        super(InternalServerException, self).__init__(message)
