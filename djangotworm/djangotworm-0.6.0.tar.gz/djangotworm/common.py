from types import MethodType
from django.db.models.query import ModelIterable
from .decorators import make_asynclike_instance


class AsyncIterator:
    def __init__(self, objects):
        self.iter = iter(objects)

    async def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.iter)
        except StopIteration:
            raise StopAsyncIteration


class TwModelIterable(ModelIterable):
    def __iter__(self):
        for obj in super(TwModelIterable, self).__iter__():
            if not getattr(obj, '_save_changed', False):
                obj.save = MethodType(make_asynclike_instance(obj.save), obj)
                obj._save_changed = True
            yield obj