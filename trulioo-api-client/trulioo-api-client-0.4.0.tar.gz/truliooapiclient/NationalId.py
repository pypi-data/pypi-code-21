"""
Auto-generated class for NationalId
"""
from .NationalIdTypes import NationalIdTypes

from . import client_support


class NationalId(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(CityOfIssue=None, CountyOfIssue=None, DistrictOfIssue=None,
               Number=None, ProvinceOfIssue=None, Type=None):
        """
        :type CityOfIssue: str
        :type CountyOfIssue: str
        :type DistrictOfIssue: str
        :type Number: str
        :type ProvinceOfIssue: str
        :type Type: NationalIdTypes
        :rtype: NationalId
        """

        return NationalId(
            CityOfIssue=CityOfIssue,
            CountyOfIssue=CountyOfIssue,
            DistrictOfIssue=DistrictOfIssue,
            Number=Number,
            ProvinceOfIssue=ProvinceOfIssue,
            Type=Type,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'NationalId'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'CityOfIssue'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.CityOfIssue = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'CountyOfIssue'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.CountyOfIssue = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'DistrictOfIssue'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.DistrictOfIssue = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Number'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.Number = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'ProvinceOfIssue'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.ProvinceOfIssue = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Type'
        val = data.get(property_name)
        if val is not None:
            datatypes = [NationalIdTypes]
            try:
                self.Type = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
