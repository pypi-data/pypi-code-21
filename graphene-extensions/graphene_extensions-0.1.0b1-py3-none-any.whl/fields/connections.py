from typing import Type

from graphql.execution.base import ResolveInfo

from graphene.relay import Connection, ConnectionField

from graphene_extensions.optimization import get_queryset
from graphene_extensions.utils.selectors import get_selectors_from_info, strip_relay_selectors

from django.db.models import Manager, Model, QuerySet


class ModelConnectionField(ConnectionField):
    @classmethod
    def connection_resolver(cls, resolver, connection_type, root, info, **kwargs):
        return super().connection_resolver(resolver, connection_type, root, info, connection_info=info, **kwargs)

    @classmethod
    def resolve_connection(cls, connection_type, args, resolved):
        if isinstance(resolved, Manager):
            resolved = resolved.get_queryset()
        else:
            model: Type[Model] = connection_type._meta.node._meta.model
            resolved = cls.get_initial_queryset(model, args['connection_info'])
        return super().resolve_connection(connection_type, args, resolved)

    @property
    def type(self) -> Type[Connection]:
        return self._type._meta.connection

    @classmethod
    def get_initial_queryset(cls, model: Type[Model], info: ResolveInfo) -> QuerySet:
        selectors = get_selectors_from_info(info)
        manager: Type[Manager] = model._default_manager
        return get_queryset(manager, strip_relay_selectors(selectors))
