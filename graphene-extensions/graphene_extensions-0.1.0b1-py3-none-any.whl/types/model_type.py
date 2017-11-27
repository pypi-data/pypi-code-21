import collections
from typing import Type, Dict, Any
from inspect import isclass

from graphene import relay
from graphene.types.base import BaseType
from graphene.types.mountedtype import MountedType
from graphene.types.objecttype import ObjectType, ObjectTypeOptions

from django.db import models

from graphene_extensions.utils.callables import get_properties, get_methods
from graphene_extensions.utils.model_meta import get_fields
from .registry import TypeRegistry, ModelRegistry


class ModelTypeOptions(ObjectTypeOptions):
    model: Type[models.Model] = None
    connection: Type[relay.Connection] = None


class ModelType(ObjectType):
    @classmethod
    def __init_subclass_with_meta__(cls, interfaces=(), possible_types=(), default_resolver=None, _meta=None,
                                    model=None, fields=None, exclude_fields=None, connection=None,
                                    **options):
        if not _meta:
            _meta = ModelTypeOptions(cls)
            _meta.model = cls.resolve_model(model)
            _meta.connection = connection or cls.create_connection()
            _meta.fields = cls.resolve_fields(model, fields, exclude_fields)
        cls.validate_meta(_meta)
        cls.register_model(model)
        super().__init_subclass_with_meta__(interfaces, possible_types, default_resolver, _meta, **options)

    def resolve_id(self, info):  # used to determine ID field when using relay.Node interface
        return self.pk

    @classmethod
    def register_model(cls, model) -> None:
        ModelRegistry().register(model, cls)

    @classmethod
    def create_connection(cls) -> Type[relay.Connection]:
        return relay.Connection.create_type(class_name=f'{cls.__name__}Connection', node=cls)

    @classmethod
    def validate_meta(cls, _meta: ModelTypeOptions) -> None:
        assert isinstance(_meta, ModelTypeOptions), \
            f'class {_meta.__name__} must derive from ModelObjectTypeOptions'

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
    def resolve_model(cls, model):
        cls.validate_model(model)
        return model

    @classmethod
    def validate_model(cls, model):
        assert isclass(model) and issubclass(model, models.Model), \
            f'Meta.model must be a valid Django Model class, received {model}'
        assert not isinstance(model, models.Model), f'Meta.model must be a Django Model class, not instance'
