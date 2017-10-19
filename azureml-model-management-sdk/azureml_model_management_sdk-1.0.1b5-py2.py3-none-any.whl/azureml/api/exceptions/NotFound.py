# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azureml.api.exceptions.ClientSideException import ClientSideException


class NotFoundException(ClientSideException):
    @property
    def status_code(self):
        return 404

    def __init__(self, message):
        super(NotFoundException, self).__init__(message)
