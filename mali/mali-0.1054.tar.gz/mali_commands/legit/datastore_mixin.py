# coding=utf-8
from .connection_mixin import ConnectionMixin


class DatastoreMixin(ConnectionMixin):
    def _build_key(self, datastore, name):
        org_name = self.__connection.data_volume_config.org
        parent_key = datastore.key('DataVolume', self.__connection.data_volume_config.name, namespace=org_name)

        return datastore.key(self._entity_kind, name, parent=parent_key, namespace=org_name)

    @property
    def _entity_kind(self):
        raise NotImplementedError(self._entity_kind)
