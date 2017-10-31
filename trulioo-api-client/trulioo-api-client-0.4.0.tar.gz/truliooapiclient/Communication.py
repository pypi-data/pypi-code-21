"""
Auto-generated class for Communication
"""

from . import client_support


class Communication(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(EmailAddress=None, MobileNumber=None, Telephone2=None, Telephone=None):
        """
        :type EmailAddress: str
        :type MobileNumber: str
        :type Telephone: str
        :type Telephone2: str
        :rtype: Communication
        """

        return Communication(
            EmailAddress=EmailAddress,
            MobileNumber=MobileNumber,
            Telephone=Telephone,
            Telephone2=Telephone2,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Communication'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'EmailAddress'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.EmailAddress = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'MobileNumber'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.MobileNumber = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Telephone'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.Telephone = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Telephone2'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.Telephone2 = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
