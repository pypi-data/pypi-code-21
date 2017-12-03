# -*- coding: utf8 -*-
from ..dulwich.object_store import BaseObjectStore


class NullObjectStore(BaseObjectStore):
    def add_objects(self, objects):
        pass

    def __iter__(self):
        pass

    def contains_packed(self, sha):
        pass

    @property
    def packs(self):
        pass

    def contains_loose(self, sha):
        pass

    def add_object(self, obj):
        pass

    def get_raw(self, name):
        raise KeyError()
