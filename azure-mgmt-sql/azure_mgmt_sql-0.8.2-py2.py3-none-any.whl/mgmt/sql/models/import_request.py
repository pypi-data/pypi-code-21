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

from .export_request import ExportRequest


class ImportRequest(ExportRequest):
    """Import database parameters.

    :param storage_key_type: The type of the storage key to use. Possible
     values include: 'StorageAccessKey', 'SharedAccessKey'
    :type storage_key_type: str or ~azure.mgmt.sql.models.StorageKeyType
    :param storage_key: The storage key to use.  If storage key type is
     SharedAccessKey, it must be preceded with a "?."
    :type storage_key: str
    :param storage_uri: The storage uri to use.
    :type storage_uri: str
    :param administrator_login: The name of the SQL administrator.
    :type administrator_login: str
    :param administrator_login_password: The password of the SQL
     administrator.
    :type administrator_login_password: str
    :param authentication_type: The authentication type. Possible values
     include: 'SQL', 'ADPassword'. Default value: "SQL" .
    :type authentication_type: str or
     ~azure.mgmt.sql.models.AuthenticationType
    :param database_name: The name of the database to import.
    :type database_name: str
    :param edition: The edition for the database being created. Possible
     values include: 'Web', 'Business', 'Basic', 'Standard', 'Premium', 'Free',
     'Stretch', 'DataWarehouse', 'System', 'System2'
    :type edition: str or ~azure.mgmt.sql.models.DatabaseEdition
    :param service_objective_name: The name of the service objective to assign
     to the database. Possible values include: 'Basic', 'S0', 'S1', 'S2', 'S3',
     'P1', 'P2', 'P3', 'P4', 'P6', 'P11', 'P15', 'System', 'System2',
     'ElasticPool'
    :type service_objective_name: str or
     ~azure.mgmt.sql.models.ServiceObjectiveName
    :param max_size_bytes: The maximum size for the newly imported database.
    :type max_size_bytes: str
    """

    _validation = {
        'storage_key_type': {'required': True},
        'storage_key': {'required': True},
        'storage_uri': {'required': True},
        'administrator_login': {'required': True},
        'administrator_login_password': {'required': True},
        'database_name': {'required': True},
        'edition': {'required': True},
        'service_objective_name': {'required': True},
        'max_size_bytes': {'required': True},
    }

    _attribute_map = {
        'storage_key_type': {'key': 'storageKeyType', 'type': 'StorageKeyType'},
        'storage_key': {'key': 'storageKey', 'type': 'str'},
        'storage_uri': {'key': 'storageUri', 'type': 'str'},
        'administrator_login': {'key': 'administratorLogin', 'type': 'str'},
        'administrator_login_password': {'key': 'administratorLoginPassword', 'type': 'str'},
        'authentication_type': {'key': 'authenticationType', 'type': 'AuthenticationType'},
        'database_name': {'key': 'databaseName', 'type': 'str'},
        'edition': {'key': 'edition', 'type': 'str'},
        'service_objective_name': {'key': 'serviceObjectiveName', 'type': 'str'},
        'max_size_bytes': {'key': 'maxSizeBytes', 'type': 'str'},
    }

    def __init__(self, storage_key_type, storage_key, storage_uri, administrator_login, administrator_login_password, database_name, edition, service_objective_name, max_size_bytes, authentication_type="SQL"):
        super(ImportRequest, self).__init__(storage_key_type=storage_key_type, storage_key=storage_key, storage_uri=storage_uri, administrator_login=administrator_login, administrator_login_password=administrator_login_password, authentication_type=authentication_type)
        self.database_name = database_name
        self.edition = edition
        self.service_objective_name = service_objective_name
        self.max_size_bytes = max_size_bytes
