"""
Auto-generated class for Record
"""
from .DatasourceResult import DatasourceResult
from .RecordRule import RecordRule
from .RecordStatus import RecordStatus
from .ServiceError import ServiceError

from . import client_support


class Record(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(DatasourceResults, Errors, RecordStatus, Rule, TransactionRecordID):
        """
        :type DatasourceResults: list[DatasourceResult]
        :type Errors: list[ServiceError]
        :type RecordStatus: RecordStatus
        :type Rule: RecordRule
        :type TransactionRecordID: str
        :rtype: Record
        """

        return Record(
            DatasourceResults=DatasourceResults,
            Errors=Errors,
            RecordStatus=RecordStatus,
            Rule=Rule,
            TransactionRecordID=TransactionRecordID,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Record'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'DatasourceResults'
        val = data.get(property_name)
        if val is not None:
            datatypes = [DatasourceResult]
            try:
                self.DatasourceResults = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

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

        property_name = 'RecordStatus'
        val = data.get(property_name)
        if val is not None:
            datatypes = [RecordStatus]
            try:
                self.RecordStatus = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'Rule'
        val = data.get(property_name)
        if val is not None:
            datatypes = [RecordRule]
            try:
                self.Rule = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'TransactionRecordID'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.TransactionRecordID = client_support.val_factory(val, datatypes)
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
