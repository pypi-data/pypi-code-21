# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azureml.api.exceptions.ClientSideException import ClientSideException


class UnsupportedMediaTypeException(ClientSideException):
    @property
    def status_code(self):
        return 415

    def __init__(self, message):
        super(UnsupportedMediaTypeException, self).__init__(message)
