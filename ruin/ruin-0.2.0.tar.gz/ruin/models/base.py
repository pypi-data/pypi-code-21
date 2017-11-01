# -*- coding: utf-8 -*-

from copy import deepcopy
from datetime import datetime

from bson import ObjectId

from ..io.encoders import str_to_date
from ..io.slug import create_unique_slug
from ..io.utils import camel_to_underscores, document_etag
from ..io.validator import Validator


class BaseModel(Validator):

    ID_FIELD = '_id'
    CREATED_FIELD = '_created'
    UPDATED_FIELD = '_updated'
    ETAG_FIELD = '_etag'
    SLUG_FIELD = 'slug'
    SLUG_VALUE_FIELDS = None

    COLLECTION_NAME = None  # Defaults to class name without 'Model'

    SPECIAL_FIELDS = (CREATED_FIELD, UPDATED_FIELD, ETAG_FIELD)

    DEFAULT_FIELDS = {}

    SCHEMA = {
        ID_FIELD: {
            'type': 'objectid',
            'coerce': ObjectId,
        },
        CREATED_FIELD: {
            'type': 'datetime',
            'coerce': str_to_date,
        },
        UPDATED_FIELD: {
            'type': 'datetime',
            'coerce': str_to_date,
        },
        ETAG_FIELD: {
            'type': 'string',
        },
    }
    document = None

    def __init__(self, data=None, *args, **kwargs):
        schema = self.__get_schema_from_parents()
        schema.update(self.SCHEMA)
        self.SCHEMA = schema  # pylint: disable=invalid-name

        if 'schema' not in kwargs:
            kwargs['schema'] = schema

        super(BaseModel, self).__init__(*args, **kwargs)
        self.data = data or {}

    def __get_schema_from_parents(self):
        schema = {}
        for base in reversed(self.__class__.__bases__):
            if issubclass(base, BaseModel):
                schema.update(deepcopy(base.SCHEMA))
        return schema

    def __repr__(self):
        return '<{}: [{}] {}>'.format(self.__class__.__name__, self.get('_id'), self.get('slug') or self.get('name', ''))

    def __getitem__(self, key):
        source = self.data if self.document is None else self.document
        return source[key]

    def get(self, key, default=None):
        source = self.data if self.document is None else self.document
        return source.get(key, default)

    def validate(self, document=None, schema=None, update=False, normalize=True):
        return super(BaseModel, self).validate(document or self.data, schema=schema, update=update, normalize=normalize)

    def set_created_field(self):
        if self.CREATED_FIELD not in self.data:
            self.data[self.CREATED_FIELD] = datetime.utcnow()

    def set_updated_field(self):
        self.data[self.UPDATED_FIELD] = datetime.utcnow()

    def set_etag_field(self):
        self.data[self.ETAG_FIELD] = document_etag(self.data)

    def set_slug_field(self, ro_database):
        if self.SLUG_FIELD and self.SLUG_VALUE_FIELDS:
            self.data[self.SLUG_FIELD] = create_unique_slug(self.data, self.SLUG_VALUE_FIELDS, ro_database, slug_key=self.SLUG_FIELD)

    def set_default_fields(self):
        if self.DEFAULT_FIELDS:
            for key, value in self.DEFAULT_FIELDS.items():
                if key not in self.SCHEMA:
                    self.SCHEMA[key] = {'default': value}
                else:
                    self.SCHEMA[key]['default'] = value

    @classmethod
    def collection_name(cls):
        if cls.COLLECTION_NAME:
            return cls.COLLECTION_NAME
        else:
            return camel_to_underscores('{}{}'.format(cls.__name__.replace('Model', ''), cls.collection_suffix()))

    @classmethod
    def collection_suffix(cls):
        """
        Override to add suffix to collection name
        """
        return ''
