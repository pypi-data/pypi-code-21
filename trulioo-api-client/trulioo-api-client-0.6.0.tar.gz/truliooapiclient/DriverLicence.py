"""
Auto-generated class for DriverLicence
"""

from . import client_support


class DriverLicence(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(DayOfExpiry=None, MonthOfExpiry=None, Number=None, State=None, YearOfExpiry=None):
        """
        :type DayOfExpiry: float
        :type MonthOfExpiry: float
        :type Number: str
        :type State: str
        :type YearOfExpiry: float
        :rtype: DriverLicence
        """

        return DriverLicence(
            DayOfExpiry=DayOfExpiry,
            MonthOfExpiry=MonthOfExpiry,
            Number=Number,
            State=State,
            YearOfExpiry=YearOfExpiry,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'DriverLicence'
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

        property_name = 'Number'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.Number = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'State'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.State = client_support.val_factory(val, datatypes)
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
