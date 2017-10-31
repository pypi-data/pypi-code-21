"""
Auto-generated class for PersonInfo
"""
from .AdditionalPersonFields import AdditionalPersonFields

from . import client_support


class PersonInfo(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(AdditionalFields, DayOfBirth, FirstGivenName, FirstSurName, Gender,
               ISOLatin1Name, MiddleName, MinimumAge, MonthOfBirth, SecondSurname, YearOfBirth):
        """
        :type AdditionalFields: AdditionalPersonFields
        :type DayOfBirth: float
        :type FirstGivenName: str
        :type FirstSurName: str
        :type Gender: str
        :type ISOLatin1Name: str
        :type MiddleName: str
        :type MinimumAge: float
        :type MonthOfBirth: float
        :type SecondSurname: str
        :type YearOfBirth: float
        :rtype: PersonInfo
        """

        return PersonInfo(
            AdditionalFields=AdditionalFields,
            DayOfBirth=DayOfBirth,
            FirstGivenName=FirstGivenName,
            FirstSurName=FirstSurName,
            Gender=Gender,
            ISOLatin1Name=ISOLatin1Name,
            MiddleName=MiddleName,
            MinimumAge=MinimumAge,
            MonthOfBirth=MonthOfBirth,
            SecondSurname=SecondSurname,
            YearOfBirth=YearOfBirth,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'PersonInfo'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'AdditionalFields'
        val = data.get(property_name)
        if val is not None:
            datatypes = [AdditionalPersonFields]
            try:
                self.AdditionalFields = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'DayOfBirth'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.DayOfBirth = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'FirstGivenName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.FirstGivenName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'FirstSurName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.FirstSurName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'Gender'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.Gender = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'ISOLatin1Name'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.ISOLatin1Name = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'MiddleName'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.MiddleName = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'MinimumAge'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.MinimumAge = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'MonthOfBirth'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.MonthOfBirth = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'SecondSurname'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.SecondSurname = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))
        else:
            raise ValueError(required_error.format(cls=class_name, prop=property_name))

        property_name = 'YearOfBirth'
        val = data.get(property_name)
        if val is not None:
            datatypes = [float]
            try:
                self.YearOfBirth = client_support.val_factory(val, datatypes)
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
