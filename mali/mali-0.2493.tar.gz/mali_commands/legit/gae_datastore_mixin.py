# -*- coding: utf8 -*-
from google.appengine.ext import ndb


class GAEDatastoreMixin(object):
    def __init__(self, org_id, volume_id):
        self.__volume_id = volume_id
        self.__org_id = org_id

    def delete_all_by_class(self, klass):
        q = klass.query(
            klass.volume_id == self._volume_id, namespace=self._org_id)

        while True:
            refs = list(q.fetch(100, keys_only=True))
            if len(refs) == 0:
                return

            ndb.delete_multi(refs)

    @property
    def _volume_id(self):
        return self.__volume_id

    @property
    def _org_id(self):
        return self.__org_id

    @classmethod
    def build_key_from_volume_id(cls, org_id, volume_id, kind, name):
        parent_key = ndb.Key('DataVolume', volume_id, namespace=org_id)

        name = name or 1

        return ndb.Key(kind, name, parent=parent_key, namespace=org_id)

    def _build_key(self, name):
        return self.build_key_from_volume_id(self.__org_id, self.__volume_id, self._entity_kind, name)

    @property
    def _entity_kind(self):
        raise NotImplementedError(self._entity_kind)
