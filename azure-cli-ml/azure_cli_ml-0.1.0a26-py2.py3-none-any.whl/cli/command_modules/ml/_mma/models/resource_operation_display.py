# coding=utf-8
# --------------------------------------------------------------------------
# Code generated by Microsoft (R) AutoRest Code Generator 1.1.0.0
# Changes may cause incorrect behavior and will be lost if the code is
# regenerated.
# --------------------------------------------------------------------------

from msrest.serialization import Model


class ResourceOperationDisplay(Model):
    """Display of the operation.

    :param provider: The resource provider name
    :type provider: str
    :param resource: The resource name
    :type resource: str
    :param operation: The operation
    :type operation: str
    :param description: The description of the operation
    :type description: str
    """

    _attribute_map = {
        'provider': {'key': 'provider', 'type': 'str'},
        'resource': {'key': 'resource', 'type': 'str'},
        'operation': {'key': 'operation', 'type': 'str'},
        'description': {'key': 'description', 'type': 'str'},
    }

    def __init__(self, provider=None, resource=None, operation=None, description=None):
        self.provider = provider
        self.resource = resource
        self.operation = operation
        self.description = description
