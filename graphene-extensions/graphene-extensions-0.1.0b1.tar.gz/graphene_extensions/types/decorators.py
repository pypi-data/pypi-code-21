import inspect
from typing import Type

import graphene
from graphene.types.base import BaseType

from .factories import CallableScalarFactory


def annotate_type(graphene_type: Type[BaseType]):
    assert issubclass(graphene_type, BaseType), \
        f'Type annotations have to of subclass graphene.BaseType, received {graphene_type}'

    def wrapper(func):
        if isinstance(func, property):
            return GrapheneProperty(func.fget, func.fget, func.fdel, func.__doc__, graphene_type=graphene_type)
        assert inspect.isfunction(func), f'@annotate_type is only supported for class methods and properties'
        assert issubclass(graphene_type, graphene.Scalar), f'@annotate_type supports only graphene Scalar\'s'
        func._graphene_type = CallableScalarFactory().get(scalar=graphene_type)
        return func

    return wrapper


def graphene_property(graphene_type: Type[BaseType]):
    assert not inspect.isfunction(graphene_type), f'@graphene_property should be initialized with a graphene type'

    assert issubclass(graphene_type, BaseType), \
        f'Type annotations have to of subclass graphene.BaseType, received {graphene_type}'

    def wrapper(func):
        return GrapheneProperty(func, graphene_type=graphene_type)

    return wrapper


class GrapheneProperty(property):
    def __init__(self, *args, **kwargs):
        self._graphene_type = kwargs.pop('graphene_type')
        super().__init__(*args, **kwargs)

    def setter(self, fset):
        raise NotImplementedError('graphene_property setter is currently not supported')
