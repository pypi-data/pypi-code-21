"""
Auto-generated class for DataFields
"""
from .Business import Business
from .Communication import Communication
from .Document import Document
from .DriverLicence import DriverLicence
from .Location import Location
from .NationalId import NationalId
from .Passport import Passport
from .PersonInfo import PersonInfo

from . import client_support


class DataFields(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(Business=None, Communication=None, Document=None, DriverLicence=None,
               Location=None, NationalIds=None, Passport=None, PersonInfo=None):
        """
        :type Business: Business
        :type Communication: Communication
        :type Document: Document
        :type DriverLicence: DriverLicence
        :type Location: Location
        :type NationalIds: list[NationalId]
        :type Passport: Passport
        :type PersonInfo: PersonInfo
        :rtype: DataFields
        """

        return DataFields(
            Business=Business,
            Communication=Communication,
            Document=Document,
            DriverLicence=DriverLicence,
            Location=Location,
            NationalIds=NationalIds,
            Passport=Passport,
            PersonInfo=PersonInfo,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'DataFields'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'Business'
        val = data.get(property_name)
        if val is not None:
            datatypes = [Business]
            try:
                self.Business = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Communication'
        val = data.get(property_name)
        if val is not None:
            datatypes = [Communication]
            try:
                self.Communication = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Document'
        val = data.get(property_name)
        if val is not None:
            datatypes = [Document]
            try:
                self.Document = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'DriverLicence'
        val = data.get(property_name)
        if val is not None:
            datatypes = [DriverLicence]
            try:
                self.DriverLicence = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Location'
        val = data.get(property_name)
        if val is not None:
            datatypes = [Location]
            try:
                self.Location = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'NationalIds'
        val = data.get(property_name)
        if val is not None:
            datatypes = [NationalId]
            try:
                self.NationalIds = client_support.list_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'Passport'
        val = data.get(property_name)
        if val is not None:
            datatypes = [Passport]
            try:
                self.Passport = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'PersonInfo'
        val = data.get(property_name)
        if val is not None:
            datatypes = [PersonInfo]
            try:
                self.PersonInfo = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
