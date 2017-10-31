"""
Auto-generated class for TransactionRecordResult
"""
from .InputField import InputField
from .Record import Record
from .ServiceError import ServiceError
from datetime import datetime

from . import client_support


class TransactionRecordResult(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(CountryCode, Errors, InputFields, ProductName, Record, TransactionID, UploadedDt):
        """
        :type CountryCode: str
        :type Errors: list[ServiceError]
        :type InputFields: list[InputField]
        :type ProductName: str
        :type Record: Record
        :type TransactionID: str
        :type UploadedDt: datetime
        :rtype: TransactionRecordResult
        """

        return TransactionRecordResult(
            CountryCode=CountryCode,
            Errors=Errors,
            InputFields=InputFields,
            ProductName=ProductName,
            Record=Record,
            TransactionID=TransactionID,
            UploadedDt=UploadedDt,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'TransactionRecordResult'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'CountryCode'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.CountryCode = client_support.val_factory(val, datatypes)
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

        property_name = 'InputFields'
        val = data.get(property_name)
        if val is not None:
            datatypes = [InputField]
            try:
                self.InputFields = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'ProductName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.ProductName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'Record'
        val = data.get(property_name)
        if val is not None:
            datatypes = [Record]
            try:
                self.Record = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'TransactionID'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.TransactionID = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'UploadedDt'
        val = data.get(property_name)
        if val is not None:
            datatypes = [datetime]
            try:
                self.UploadedDt = client_support.val_factory(val, datatypes)
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
