"""
Auto-generated class for DatasourceField
"""

from . import client_support


class DatasourceField(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(FieldName, Status, FieldGroup=None):
        """
        :type FieldGroup: str
        :type FieldName: str
        :type Status: str
        :rtype: DatasourceField
        """

        return DatasourceField(
            FieldGroup=FieldGroup,
            FieldName=FieldName,
            Status=Status,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'DatasourceField'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'FieldGroup'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.FieldGroup = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'FieldName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.FieldName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'Status'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.Status = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
