# -*- coding: utf8 -*-
from ..datastore_mixin import DatastoreMixin
from ..dulwich.refs import RefsContainer


SYMREF = b'ref: '


class DatastoreRefContainer(DatastoreMixin, RefsContainer):
    def __init__(self, connection):
        super(DatastoreRefContainer, self).__init__(connection)

    @property
    def _entity_kind(self):
        return 'DataVolumeRef'

    def get_packed_refs(self):
        return {}

    def set_if_equals(self, name, old_ref, new_ref):
        self._check_refname(name)

        name = name.decode('ascii')
        old_ref = old_ref.decode('ascii')
        new_ref = new_ref.decode('ascii')

        def txn(key):
            with datastore_client.transaction():
                ref_entity = datastore_client.get(key)

                if ref_entity is None:
                    return False

                if ref_entity['data'] != old_ref:
                    return False

                entity = self._connection.create_entity(key)
                entity['data'] = new_ref
                datastore_client.put(entity)

                return True

        with self._connection.get_cursor() as datastore_client:
            ref_key = self._build_key(datastore_client, name)

            return txn(ref_key)

    def add_if_new(self, name, ref):
        self._check_refname(name)

        name = name.decode('ascii')
        ref = ref.decode('ascii')

        def txn(key):
            with datastore_client.transaction():
                ref_entity = datastore_client.get(key)

                if ref_entity is not None:
                    return False

                entity = self._connection.create_entity(key)
                entity['data'] = ref
                datastore_client.put(entity)

                return True

        with self._connection.get_cursor() as datastore_client:
            ref_key = self._build_key(datastore_client, name)

            return txn(ref_key)

    def read_loose_ref(self, name):
        """Read a reference and return its contents.

        If the reference file a symbolic reference, only read the first line of
        the file. Otherwise, only read the first 40 bytes.

        :param name: the refname to read, relative to refpath
        :return: The contents of the ref file, or None if the file does not
            exist.
        """

        with self._connection.get_cursor() as datastore:
            ref_key = self._build_key(datastore, name.decode('utf8'))
            ref = datastore.get(ref_key)

            if ref is None:
                return None

            data = ref['data']

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
