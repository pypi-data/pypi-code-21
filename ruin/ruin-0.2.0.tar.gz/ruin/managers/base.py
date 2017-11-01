# -*- coding: utf-8 -*-

from collections import defaultdict
from copy import deepcopy
import logging as log

import pymongo

from ..db.decorators import master, slave
from ..db.query_options import QueryOptions
from ..models.base import BaseModel


class ValidationError(Exception):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.errors = None


def query_log(self, *args):
    log.debug(
        '%s(%s): %s',
        self.__class__.__name__,
        self.MODEL_CLASS.__name__,
        ', '.join([str(arg) for arg in args]))


class BaseManager:

    MODEL_CLASS = BaseModel
    DEFAULT_SORT = MODEL_CLASS.ID_FIELD
    # Query which is applied always
    BASE_QUERY = {}

    connection = None

    @classmethod
    def factory(cls, model_class, default_sort=None, base_query=None):
        """
        Factory method so we don't need to subclass every time
        """
        instance = cls()
        instance.MODEL_CLASS = model_class  # pylint: disable=invalid-name
        instance.DEFAULT_SORT = default_sort or model_class.ID_FIELD  # pylint: disable=invalid-name
        instance.BASE_QUERY = base_query or {}  # pylint: disable=invalid-name
        return instance

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)

    @master
    def rw_conn(self):
        return self.connection[self.MODEL_CLASS.collection_name()]

    @slave
    def ro_conn(self):
        return self.connection[self.MODEL_CLASS.collection_name()]

    def get(self, options):
        if isinstance(options, QueryOptions):
            pass
        elif isinstance(options, dict):
            options = QueryOptions(
                query=options
            )
        else:
            item_id = options
            options = QueryOptions(
                query={self.MODEL_CLASS.ID_FIELD: item_id}
            )

        self.__apply_base_query(options.query)

        model = self.MODEL_CLASS(options.query)
        model = self.__remove_defaults(model, options.query)

        # if not model.validate(update=True):
        #    self._validation_error(model)
        # Ignore validation errors for query
        model.validate(update=True)

        query_log(self, model.document)
        item = self.ro_conn().find_one(model.document, projection=options.projection)

        if item:
            instance = self.MODEL_CLASS(item)
            if not instance.validate(update=bool(options.projection)):
                self._log_validation_message(instance)
            return instance.data

    @staticmethod
    def __remove_defaults(model, query):
        """
        Remove default values generated for some fields.
        We don't want them to get into the query and modify it.
        It brings evil.
        """

        query = query or {}
        keys_to_remove = []
        for key, schema in model.schema.items():
            if key not in query and 'default' in schema:
                keys_to_remove.append(key)
        for key in keys_to_remove:
            del model.schema[key]
        return model

    def find(self, options=None):

        options = options or QueryOptions()

        if not isinstance(options, QueryOptions):
            raise TypeError('Options must be QueryOptions instance')

        model = self.MODEL_CLASS(options.query)
        model = self.__remove_defaults(model, options.query)

        # Ignore validation errors for query
        model.validate(update=True)

        limit = options.limit
        offset = options.offset or 0
        projection = options.projection
        sort = self.__transform_sort(options.sort or self.DEFAULT_SORT)

        self.__apply_base_query(model.document)
        query_log(self, model.document)
        query = self.ro_conn().find(model.document, projection=projection)

        if sort:
            query = query.sort(sort)

        if limit is not None:
            query = query.skip(offset).limit(limit)

        valid_items = []

        for item in query:
            instance = self.MODEL_CLASS(item)
            instance.validate()
            valid_items.append(instance.data)

            if instance.errors:
                # If projection is present, required fields are likely to be missing
                if projection:
                    for key in projection:
                        if key in instance.errors:
                            self._log_validation_message(instance)
                            break
                else:
                    self._log_validation_message(instance)

        return valid_items

    @classmethod
    def __apply_base_query(cls, query):
        """
        Adds missing attributes to query from cls.BASE_QUERY
        """
        for key, value in cls.BASE_QUERY.items():
            if key not in query:
                query[key] = value

    def _log_validation_message(self, instance):
        log.debug('Model Validation: %s [%s]', self.__class__.__name__, instance.get(self.MODEL_CLASS.ID_FIELD))

    @staticmethod
    def __transform_sort(sort):
        transformed = []
        items = [item.strip() for item in sort.split(',')]
        for item in items:
            order = pymongo.DESCENDING if item.startswith('-') else pymongo.ASCENDING
            field = item.replace('-', '')
            transformed.append((field, order))
        return transformed

    @classmethod
    def _validation_error(cls, model):
        msg = '{} is not valid'.format(cls.MODEL_CLASS.__name__)
        log.warning('%s. ERRORS: %s', msg, model.errors)
        log.warning('ERROR VALUES: %s', {key: model.document.get(key) for key in model.errors})
        err = ValidationError(msg)
        err.errors = model.errors
        raise err

    def create(self, data):
        if isinstance(data, self.MODEL_CLASS):
            model = data
        else:
            model = self.MODEL_CLASS(data)

        model.set_created_field()
        model.set_updated_field()
        model.set_etag_field()
        model.set_default_fields()

        if self.MODEL_CLASS.SLUG_FIELD not in model.data:
            model.set_slug_field(self.ro_conn())

        if not model.validate():
            self._validation_error(model)

        query_log(self, model.document)
        result = self.rw_conn().insert_one(model.document)
        model.document.update({self.MODEL_CLASS.ID_FIELD: result.inserted_id})
        model.data.update({self.MODEL_CLASS.ID_FIELD: result.inserted_id})
        return model.data

    def update(self, options, data, many=False, upsert=False, operation='$set', modifiers=None):  # pylint: disable=too-many-arguments
        modifiers = modifiers or {}
        model = self.MODEL_CLASS(data)
        model = self.__remove_defaults(model, data)

        model.set_updated_field()
        model.set_etag_field()

        if upsert:
            model.set_created_field()
            if self.MODEL_CLASS.SLUG_FIELD not in model.data:
                model.set_slug_field(self.ro_conn())

        if not model.validate(update=not upsert):
            self._validation_error(model)

        query, is_many = self._get_query_and_strategy(options)

        if is_many or many:
            update_fn = self.rw_conn().update_many
        else:
            update_fn = self.rw_conn().update_one

        update_query = self._incorporate_special_fields(model, operation, modifiers)

        query_log(self, query, update_query)
        result = update_fn(query, update_query, upsert=upsert)
        return result.modified_count

    @classmethod
    def _incorporate_special_fields(cls, model, operation, modifiers):
        """
        In case we want to make $push, it migh occur that fields like _update are added too. That means we are fucked.
        We must take care of that so we do $push and $set in one query.
        """
        query = defaultdict(dict)
        if operation == '$set':
            query['$set'] = model.document
        else:
            for field in model.SPECIAL_FIELDS:
                if field in model.document:
                    query['$set'][field] = cls._apply_modifier_dude(deepcopy(model.document), deepcopy(modifiers), key=field)
                    model.document.pop(field)
                    query[operation] = cls._apply_modifier_dude(deepcopy(model.document), deepcopy(modifiers))
        return query

    @classmethod
    def _apply_modifier_dude(cls, document, modifiers, key=None):
        if key:
            if key in modifiers:
                modifier = modifiers.pop(key)
                return modifier(document[key])
                # return {modifiers.pop(key): document[key]}
            else:
                return document[key]

        doc = {}
        for key, value in document.items():
            if key in modifiers:
                modifier = modifiers.pop(key)
                doc[key] = modifier(value)
            else:
                doc[key] = value
        return doc

    def _get_query_and_strategy(self, options):
        """
        Decides how query will look like and if we are working with single or many docs.
        """
        is_many = False
        if isinstance(options, QueryOptions):
            query = options.query
            is_many = True
        elif isinstance(options, dict):
            model = self.MODEL_CLASS(options)
            model.validate(update=True)
            query = model.document
        else:
            model = self.MODEL_CLASS({self.MODEL_CLASS.ID_FIELD: options})
            model.validate(update=True)
            query = model.document
        return query, is_many

    def delete(self, options):
        query, is_many = self._get_query_and_strategy(options)

        if is_many:
            delete_fn = self.rw_conn().delete_many
        else:
            delete_fn = self.rw_conn().delete_one

        query_log(self, query)
        result = delete_fn(query)
        return result.deleted_count

    def count(self, options=None):
        options = options or QueryOptions()

        if not isinstance(options, QueryOptions):
            raise TypeError('Options must be QueryOptions instance')

        self.__apply_base_query(options.query)
        model = self.MODEL_CLASS(options.query)
        model = self.__remove_defaults(model, options.query)

        # Ignore validation errors for query
        model.validate(update=True)

        query_log(self, model.document)
        return self.ro_conn().count(model.document)
