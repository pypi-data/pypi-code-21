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


class EditionCapability(Model):
    """The database edition capabilities.

    Variables are only populated by the server, and will be ignored when
    sending a request.

    :ivar name: The edition name.
    :vartype name: str
    :ivar status: The status of the edition. Possible values include:
     'Visible', 'Available', 'Default', 'Disabled'
    :vartype status: str or ~azure.mgmt.sql.models.CapabilityStatus
    :ivar supported_service_level_objectives: The list of supported service
     objectives for the edition.
    :vartype supported_service_level_objectives:
     list[~azure.mgmt.sql.models.ServiceObjectiveCapability]
    """

    _validation = {
        'name': {'readonly': True},
        'status': {'readonly': True},
        'supported_service_level_objectives': {'readonly': True},
    }

    _attribute_map = {
        'name': {'key': 'name', 'type': 'str'},
        'status': {'key': 'status', 'type': 'CapabilityStatus'},
        'supported_service_level_objectives': {'key': 'supportedServiceLevelObjectives', 'type': '[ServiceObjectiveCapability]'},
    }

    def __init__(self):
        self.name = None
        self.status = None
        self.supported_service_level_objectives = None
