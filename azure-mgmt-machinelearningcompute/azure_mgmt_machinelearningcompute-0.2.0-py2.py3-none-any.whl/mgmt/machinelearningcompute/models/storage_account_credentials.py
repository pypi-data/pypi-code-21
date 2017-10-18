# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#
# Code generated by Microsoft (R) AutoRest Code Generator.
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class StorageAccountCredentials(Model):
    """Access information for the storage account.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :ivar resource_id: The ARM resource ID of the storage account.
    :vartype resource_id: str
    :ivar primary_key: The primary key of the storage account.
    :vartype primary_key: str
    :ivar secondary_key: The secondary key of the storage account.
    :vartype secondary_key: str
    """

    _validation = {
        'resource_id': {'readonly': True},
        'primary_key': {'readonly': True},
        'secondary_key': {'readonly': True},
    }

    _attribute_map = {
        'resource_id': {'key': 'resourceId', 'type': 'str'},
        'primary_key': {'key': 'primaryKey', 'type': 'str'},
        'secondary_key': {'key': 'secondaryKey', 'type': 'str'},
    }

    def __init__(self):
        self.resource_id = None
        self.primary_key = None
        self.secondary_key = None
