"""
Auto-generated class for Document
"""
from .DocumentTypes import DocumentTypes

from . import client_support


class Document(object):
    """
    auto-generated. don't touch.
    """

    @staticmethod
    def create(DocumentBackImage=None, DocumentFrontImage=None, DocumentType=None, LivePhoto=None):
        """
        :type DocumentBackImage: str
        :type DocumentFrontImage: str
        :type DocumentType: DocumentTypes
        :type LivePhoto: str
        :rtype: Document
        """

        return Document(
            DocumentBackImage=DocumentBackImage,
            DocumentFrontImage=DocumentFrontImage,
            DocumentType=DocumentType,
            LivePhoto=LivePhoto,
        )

    def __init__(self, json=None, **kwargs):
        if json is None and not kwargs:
            raise ValueError('No data or kwargs present')

        class_name = 'Document'
        create_error = '{cls}: unable to create {prop} from value: {val}: {err}'
        required_error = '{cls}: missing required property {prop}'

        data = json or kwargs

        property_name = 'DocumentBackImage'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.DocumentBackImage = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'DocumentFrontImage'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.DocumentFrontImage = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'DocumentType'
        val = data.get(property_name)
        if val is not None:
            datatypes = [DocumentTypes]
            try:
                self.DocumentType = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

        property_name = 'LivePhoto'
        val = data.get(property_name)
        if val is not None:
            datatypes = [str]
            try:
                self.LivePhoto = client_support.val_factory(val, datatypes)
            except ValueError as err:
                raise ValueError(create_error.format(cls=class_name, prop=property_name, val=val, err=err))

    def __str__(self):
        return self.as_json(indent=4)

    def as_json(self, indent=0):
        return client_support.to_json(self, indent=indent)

    def as_dict(self):
        return client_support.to_dict(self)
