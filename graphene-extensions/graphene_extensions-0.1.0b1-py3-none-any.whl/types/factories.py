from typing import Type

import graphene

from graphene_extensions.utils import Singleton


class CallableScalarFactory(metaclass=Singleton):
    registered_scalars = {}

    def get(self, scalar: Type[graphene.Scalar]):
        assert issubclass(scalar, graphene.Scalar), f'Callable fields have to of type Scalar, received {scalar}'

        if scalar in self.registered_scalars:
            return self.registered_scalars[scalar]
        return self.register_scalar(scalar)

    def register_scalar(self, scalar: Type[graphene.Scalar]):
        class_name = f'Callable{scalar.__name__}'

        class CallableScalar(scalar):
            class Meta:
                name = class_name

            @staticmethod
            def serialize_callable(value):
                return scalar.serialize(value())

            serialize = serialize_callable

        CallableScalar.__name__ = class_name
        self.registered_scalars[scalar] = CallableScalar
        return self.registered_scalars[scalar]
