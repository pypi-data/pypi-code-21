"""
Auto-generated class for VerifyRequest
"""
from .DataFields import DataFields

from . import client_support


class VerifyRequest(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(AcceptTruliooTermsAndConditions, CleansedAddress, ConfigurationName, ConsentForDataSources,
               DataFields, VerboseMode, CallBackUrl=None, CountryCode=None, Demo=None, Timeout=None):
        """
        :type AcceptTruliooTermsAndConditions: bool
        :type CallBackUrl: str
        :type CleansedAddress: bool
        :type ConfigurationName: str
        :type ConsentForDataSources: list[str]
        :type CountryCode: str
        :type DataFields: DataFields
        :type Demo: bool
        :type Timeout: float
        :type VerboseMode: bool
        :rtype: VerifyRequest
        """

        return VerifyRequest(
            AcceptTruliooTermsAndConditions=AcceptTruliooTermsAndConditions,
            CallBackUrl=CallBackUrl,
            CleansedAddress=CleansedAddress,
            ConfigurationName=ConfigurationName,
            ConsentForDataSources=ConsentForDataSources,
            CountryCode=CountryCode,
            DataFields=DataFields,
            Demo=Demo,
            Timeout=Timeout,
            VerboseMode=VerboseMode,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'VerifyRequest'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'AcceptTruliooTermsAndConditions'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.AcceptTruliooTermsAndConditions = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'CallBackUrl'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.CallBackUrl = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'CleansedAddress'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.CleansedAddress = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'ConfigurationName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.ConfigurationName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'ConsentForDataSources'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.ConsentForDataSources = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'CountryCode'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.CountryCode = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'DataFields'
        val = data.get(property_name)
        if val is not None:
            datatypes = [DataFields]
            try:
                self.DataFields = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'Demo'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.Demo = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Timeout'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.Timeout = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'VerboseMode'
        val = data.get(property_name)
        if val is not None:
            datatypes = [bool]
            try:
                self.VerboseMode = client_support.val_factory(val, datatypes)
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
