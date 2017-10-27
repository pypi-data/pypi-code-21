"""Process resource."""
from __future__ import absolute_import, division, print_function, unicode_literals

from .base import BaseResolweResource


class DescriptorSchema(BaseResolweResource):
    """Resolwe DescriptorSchema resource.

    One and only one of the identifiers (slug, id or model_data)
    should be given.

    :param resolwe: Resolwe instance
    :type resolwe: Resolwe object
    :param model_data: Resource model data

    """

    endpoint = "descriptorschema"

    WRITABLE_FIELDS = ('description',) + BaseResolweResource.WRITABLE_FIELDS
    READ_ONLY_FIELDS = ('schema',) + BaseResolweResource.READ_ONLY_FIELDS

    ALL_PERMISSIONS = ['view', 'edit', 'share', 'owner']

    def __init__(self, resolwe, **model_data):
        """Initialize attributes."""
        self.data_name = None
        """
        the default name of data object using this process. When data object
        is created you can assign a name to it. But if you don't, the name of
        data object is determined from this field. The field is a expression
        which can take values of other fields.
        """
        #: descriptor schema description
        self.description = None
        #: specification of descriptor schema
        self.schema = None

        super(DescriptorSchema, self).__init__(resolwe, **model_data)
