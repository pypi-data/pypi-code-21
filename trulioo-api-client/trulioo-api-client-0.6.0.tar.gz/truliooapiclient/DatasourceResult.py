"""
Auto-generated class for DatasourceResult
"""
from .AppendedField import AppendedField
from .DatasourceField import DatasourceField
from .ServiceError import ServiceError

from . import client_support


class DatasourceResult(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(AppendedFields, DatasourceFields, DatasourceName, Errors, FieldGroups, DatasourceStatus=None):
        """
        :type AppendedFields: list[AppendedField]
        :type DatasourceFields: list[DatasourceField]
        :type DatasourceName: str
        :type DatasourceStatus: str
        :type Errors: list[ServiceError]
        :type FieldGroups: list[str]
        :rtype: DatasourceResult
        """

        return DatasourceResult(
            AppendedFields=AppendedFields,
            DatasourceFields=DatasourceFields,
            DatasourceName=DatasourceName,
            DatasourceStatus=DatasourceStatus,
            Errors=Errors,
            FieldGroups=FieldGroups,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'DatasourceResult'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'AppendedFields'
        val = data.get(property_name)
        if val is not None:
            datatypes = [AppendedField]
            try:
                self.AppendedFields = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'DatasourceFields'
        val = data.get(property_name)
        if val is not None:
            datatypes = [DatasourceField]
            try:
                self.DatasourceFields = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'DatasourceName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.DatasourceName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'DatasourceStatus'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.DatasourceStatus = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Errors'
        val = data.get(property_name)
        if val is not None:
            datatypes = [ServiceError]
            try:
                self.Errors = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'FieldGroups'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.FieldGroups = client_support.list_factory(val, datatypes)
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
