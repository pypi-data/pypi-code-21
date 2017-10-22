# coding=utf-8
from google.appengine.ext import ndb
from .connection_mixin import ConnectionMixin


class GAEDatastoreMixin(ConnectionMixin):
    @classmethod
    def build_key_from_volume_id(cls, org_id, volume_id, kind, name):
        parent_key = ndb.Key('DataVolume', volume_id, namespace=org_id)

        name = name or 1

        return ndb.Key(kind, name, parent=parent_key, namespace=org_id)

    def _build_key(self, name):
        return self.build_key_from_volume_id(
            self._connection.data_volume_config.org,
            self._connection.data_volume_config.volume_id, self._entity_kind, name)

    @property
    def _entity_kind(self):
        raise NotImplementedError(self._entity_kind)
