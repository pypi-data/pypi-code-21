# -*- coding: utf8 -*-
import logging

from google.appengine.ext import ndb

from ..gae_datastore_mixin import GAEDatastoreMixin
from ..dulwich.refs import RefsContainer


SYMREF = b'ref: '


class DataVolumeRefModel(ndb.Model):
    data = ndb.StringProperty(required=True)
    volume_id = ndb.IntegerProperty()  # This is a new prop its needs to be required but for backward support it can't

    @classmethod
    def _get_kind(cls):
        return 'Ref'


class GAEDatastoreRefContainer(GAEDatastoreMixin, RefsContainer):
    def __init__(self, org_id, volume_id):
        super(GAEDatastoreRefContainer, self).__init__(org_id, volume_id)

    def close(self):
        pass

    def delete_all(self):
        self.delete_all_by_class(DataVolumeRefModel)

    @property
    def _entity_kind(self):
        return 'Ref'

    def get_packed_refs(self):
        return {}

    def __add_or_set(self, name, on_ref_entity):
        logging.info('__add_or_set %s', name)

        self._check_refname(name)

        name = name.decode('ascii')

        @ndb.transactional()
        def txn():
            key = self._build_key(name)
            ref_entity = key.get()

            return on_ref_entity(key, ref_entity)

        return txn()

    def set_if_equals(self, name, old_ref, new_ref):
        logging.debug('set_if_equals %s %s %s', name, old_ref, new_ref)

        old_ref = old_ref.decode('ascii')
        new_ref = new_ref.decode('ascii')

        def on_ref_entity(key, ref_entity):
            if ref_entity is None:
                return False

            if ref_entity.data != old_ref:
                return False

            ref_entity.data = new_ref
            ref_entity.put()

            return True

        return self.__add_or_set(name, on_ref_entity)

    def add_if_new(self, name, ref):
        logging.debug('add_if_new %s %s', name, ref)

        ref = ref.decode('ascii')

        def on_ref_entity(key, ref_entity):
            if ref_entity is not None:
                return False

            DataVolumeRefModel(key=key, data=ref, volume_id=self._volume_id).put()

            return True

        return self.__add_or_set(name, on_ref_entity)

    def read_loose_ref(self, name):
        """Read a reference and return its contents.

        If the reference file a symbolic reference, only read the first line of
        the file. Otherwise, only read the first 40 bytes.

        :param name: the refname to read, relative to refpath
        :return: The contents of the ref file, or None if the file does not
            exist.
        """

        ref_key = self._build_key(name.decode('utf8'))
        ref = ref_key.get()

        if ref is None:
            return None

        data = ref.data

        header = data[:len(SYMREF)]
        if header == SYMREF:
            # Read only the first line
            return data.splitlines()[0]

        # Read only the first 40 bytes
        return data[:40].encode('ascii')

    def set_symbolic_ref(self, name, other):
        raise NotImplementedError(self.set_symbolic_ref)

    def allkeys(self):
        raise NotImplementedError(self.allkeys)

    def remove_if_equals(self, name, old_ref):
        raise NotImplementedError(self.remove_if_equals)
