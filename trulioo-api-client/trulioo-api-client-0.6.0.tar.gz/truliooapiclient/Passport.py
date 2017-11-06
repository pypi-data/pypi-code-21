"""
Auto-generated class for Passport
"""

from . import client_support


class Passport(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(DayOfExpiry=None, MonthOfExpiry=None, Mrz1=None, Mrz2=None, Number=None, YearOfExpiry=None):
        """
        :type DayOfExpiry: float
        :type MonthOfExpiry: float
        :type Mrz1: str
        :type Mrz2: str
        :type Number: str
        :type YearOfExpiry: float
        :rtype: Passport
        """

        return Passport(
            DayOfExpiry=DayOfExpiry,
            MonthOfExpiry=MonthOfExpiry,
            Mrz1=Mrz1,
            Mrz2=Mrz2,
            Number=Number,
            YearOfExpiry=YearOfExpiry,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Passport'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'DayOfExpiry'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.DayOfExpiry = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'MonthOfExpiry'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.MonthOfExpiry = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Mrz1'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.Mrz1 = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Mrz2'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.Mrz2 = client_support.val_factory(val, datatypes)
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

        property_name = 'YearOfExpiry'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.YearOfExpiry = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
