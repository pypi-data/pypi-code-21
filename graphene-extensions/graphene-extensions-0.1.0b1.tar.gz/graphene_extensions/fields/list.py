from functools import partial

import graphene


class ModelListField(graphene.Field):
    def __init__(self, type_, *args, **kwargs):
        super().__init__(graphene.List[type_], *args, **kwargs)

    @staticmethod
    def list_resolver(resolver, root, info, **kwargs):
        raise NotImplementedError()

    def get_resolver(self, parent_resolver):
        return partial(self.list_resolver, parent_resolver)
