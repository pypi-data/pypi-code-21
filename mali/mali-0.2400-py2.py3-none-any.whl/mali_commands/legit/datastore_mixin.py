# -*- coding: utf8 -*-


class DatastoreMixin(object):
    def __init__(self, org_id, volume_id):
        self.__org_id = org_id
        self.__volume_id = volume_id

    def _build_key(self, datastore, name):
        org_name = self.__org_id
        parent_key = datastore.key('DataVolume', self.__volume_id, namespace=org_name)

        return datastore.key(self._entity_kind, name, parent=parent_key, namespace=org_name)

    @property
    def _entity_kind(self):
        raise NotImplementedError(self._entity_kind)
