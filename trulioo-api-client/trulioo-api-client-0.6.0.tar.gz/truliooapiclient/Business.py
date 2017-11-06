"""
Auto-generated class for Business
"""

from . import client_support


class Business(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(BusinessName=None, BusinessRegistrationNumber=None, DayOfIncorporation=None,
               MonthOfIncorporation=None, YearOfIncorporation=None):
        """
        :type BusinessName: str
        :type BusinessRegistrationNumber: str
        :type DayOfIncorporation: float
        :type MonthOfIncorporation: float
        :type YearOfIncorporation: float
        :rtype: Business
        """

        return Business(
            BusinessName=BusinessName,
            BusinessRegistrationNumber=BusinessRegistrationNumber,
            DayOfIncorporation=DayOfIncorporation,
            MonthOfIncorporation=MonthOfIncorporation,
            YearOfIncorporation=YearOfIncorporation,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Business'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'BusinessName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.BusinessName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'BusinessRegistrationNumber'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.BusinessRegistrationNumber = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'DayOfIncorporation'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.DayOfIncorporation = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'MonthOfIncorporation'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.MonthOfIncorporation = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'YearOfIncorporation'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.YearOfIncorporation = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
