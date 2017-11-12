# coding=utf-8
from google.appengine.ext import ndb


class GAEDatastoreMixin(object):
    def __init__(self, org_id, volume_id):
        self.__volume_id = volume_id
        self.__org_id = org_id

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
