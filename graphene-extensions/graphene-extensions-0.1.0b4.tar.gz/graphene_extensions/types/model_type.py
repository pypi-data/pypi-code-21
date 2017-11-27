import collections
from typing import Type, Dict, Any
from inspect import isclass

from django.db import models

import graphene
from graphene import relay
from graphene.types.base import BaseType
from graphene.types.mountedtype import MountedType
from graphene.types.objecttype import ObjectType, ObjectTypeOptions

from graphene_extensions.utils.callables import get_properties, get_methods
from graphene_extensions.utils.model_meta import get_fields
from graphene_extensions.fields import ModelConnectionField, ModelListField

from .registry import TypeRegistry, ModelRegistry


class ModelTypeOptions(ObjectTypeOptions):
    def __init__(self, class_type, model, fields, exclude_fields, connection):
        super().__init__(class_type)
        self.connection: Type[relay.Connection] = connection or self.create_connection()
        self.model: Type[models.Model] = self.resolve_model(model)
        self.fields = self.resolve_fields(model, fields, exclude_fields)
        self.register_model()

    def register_model(self) -> None:
        ModelRegistry().register(self.model, self.class_type)

    def create_connection(self) -> Type[relay.Connection]:
        return relay.Connection.create_type(class_name=f'{self.class_type.__name__}Connection', node=self.class_type)

    def resolve_model(self, model):
        self.validate_model(model)
        return model

    @classmethod
    def validate_model(cls, model):
        assert isclass(model) and issubclass(model, models.Model), \
            f'Meta.model must be a valid Django Model class, received {model}'
        assert not isinstance(model, models.Model), f'Meta.model must be a Django Model class, not instance'

    @classmethod
    def resolve_fields(cls, model: Type[models.Model], fields, exclude_fields) -> Dict[str, BaseType]:
        resolved_fields = collections.OrderedDict()
        model_fields = cls.get_model_fields(model)

        assert not (fields and exclude_fields), f'Using "fields" and "exclude_fields" together is ambiguous'
        if exclude_fields:
            fields = [field for field in model_fields.keys() if field not in exclude_fields]
        if fields == '__all__':
            fields = tuple(model_fields.keys())

        cls.validate_fields(model_fields, fields)
        for field in fields:
            try:
                resolved_fields[field] = cls.get_graphene_type(model_fields[field])
            except AssertionError as e:
                raise AssertionError(f'{field}: {e}')
        return resolved_fields

    @classmethod
    def get_graphene_type(cls, field: models.Field) -> MountedType:
        return TypeRegistry().get(field)

    @classmethod
    def validate_fields(cls, model_fields: dict, fields) -> None:
        message = f'Meta.fields must be either a Tuple/List of model field names or "__all__"'
        if isinstance(fields, (list, tuple)):
            for field in fields:
                assert isinstance(field, str), f'Field name should be of type str, received {field}'
                assert field in model_fields, f'Invalid field "{field}", options are: {tuple(model_fields.keys())}'
        else:
            raise AssertionError(message)

    @classmethod
    def get_model_fields(cls, model: Type[models.Model]) -> Dict[str, Any]:
        return {**get_properties(model),
                **get_methods(model, skip=['clean', 'get_deferred_fields']),
                **get_fields(model)}


class ModelType(ObjectType):
    @classmethod
    def __init_subclass_with_meta__(cls, interfaces=(), possible_types=(), default_resolver=None, _meta=None,
                                    model=None, fields=None, exclude_fields=None, connection=None,
                                    **options):
        if not _meta:
            _meta = ModelTypeOptions(cls, model, fields, exclude_fields, connection)
        cls.validate_meta(_meta)
        super().__init_subclass_with_meta__(interfaces, possible_types, default_resolver, _meta, **options)

    def resolve_id(self, info):  # used to determine ID field when using relay.Node interface
        return self.pk

    @classmethod
    def validate_meta(cls, _meta: ModelTypeOptions) -> None:
        assert isinstance(_meta, ModelTypeOptions), \
            f'class {_meta.__name__} must derive from ModelObjectTypeOptions'

    @classmethod
    def using_relay(cls):
        return any(issubclass(i, graphene.Node) for i in cls._meta.interfaces)

    @classmethod
    def get_field_class(cls, many: bool) -> Type[graphene.Field]:
        if not many:
            return graphene.Field
        return ModelConnectionField if cls.using_relay() else ModelListField
