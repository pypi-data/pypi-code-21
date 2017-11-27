from typing import Type
from functools import partial

from django.db.models import Manager, Model, QuerySet

from graphql import ResolveInfo

import graphene

from graphene_extensions.optimization import get_queryset
from graphene_extensions.utils.selectors import strip_relay_selectors, get_selectors_from_info


class ModelListField(graphene.Field):
    def __init__(self, type_, *args, **kwargs):
        super().__init__(graphene.List(type_), *args, **kwargs)

    @property
    def model(self):
        return self.type.of_type._meta.model

    @classmethod
    def list_resolver(cls, resolver, model, root, info, **kwargs):
        resolved = resolver(root, info, **kwargs)
        if not resolved:
            return cls.get_initial_queryset(model, info)
        assert isinstance(resolved, Manager), f'ModelListField expected Manager, got {resolved}'
        return resolved.get_queryset()

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, parent_resolver, self.model)

    @classmethod
    def get_initial_queryset(cls, model: Type[Model], info: ResolveInfo) -> QuerySet:
        return get_queryset(model, strip_relay_selectors(get_selectors_from_info(info)))
