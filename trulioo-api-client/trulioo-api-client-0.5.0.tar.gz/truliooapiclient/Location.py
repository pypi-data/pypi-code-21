"""
Auto-generated class for Location
"""
from .AdditionalAddressFields import AdditionalAddressFields

from . import client_support


class Location(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(AdditionalFields=None, BuildingName=None, BuildingNumber=None, City=None, Country=None, County=None,
               POBox=None, PostalCode=None, StateProvinceCode=None, StreetName=None, StreetType=None, Suburb=None, UnitNumber=None):
        """
        :type AdditionalFields: AdditionalAddressFields
        :type BuildingName: str
        :type BuildingNumber: str
        :type City: str
        :type Country: str
        :type County: str
        :type POBox: str
        :type PostalCode: str
        :type StateProvinceCode: str
        :type StreetName: str
        :type StreetType: str
        :type Suburb: str
        :type UnitNumber: str
        :rtype: Location
        """

        return Location(
            AdditionalFields=AdditionalFields,
            BuildingName=BuildingName,
            BuildingNumber=BuildingNumber,
            City=City,
            Country=Country,
            County=County,
            POBox=POBox,
            PostalCode=PostalCode,
            StateProvinceCode=StateProvinceCode,
            StreetName=StreetName,
            StreetType=StreetType,
            Suburb=Suburb,
            UnitNumber=UnitNumber,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Location'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'AdditionalFields'
        val = data.get(property_name)
        if val is not None:
            datatypes = [AdditionalAddressFields]
            try:
                self.AdditionalFields = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'BuildingName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.BuildingName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'BuildingNumber'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.BuildingNumber = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'City'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.City = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Country'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.Country = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'County'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.County = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'POBox'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.POBox = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'PostalCode'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.PostalCode = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'StateProvinceCode'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.StateProvinceCode = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'StreetName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.StreetName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'StreetType'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.StreetType = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Suburb'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.Suburb = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'UnitNumber'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.UnitNumber = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
