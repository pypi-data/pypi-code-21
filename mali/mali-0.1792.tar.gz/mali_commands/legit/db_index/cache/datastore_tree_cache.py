# coding=utf-8
from ...datastore_mixin import DatastoreMixin
from .tree_cache import TreeCache


class DatastoreTreeCache(DatastoreMixin, TreeCache):
    def __init__(self, connection):
        self.__connection = connection
        org_id = self.__connection.data_volume_config.org
        volume_id = self.__connection.data_volume_config.volume_id

        super(DatastoreTreeCache, self).__init__(org_id, volume_id)

    @property
    def _entity_kind(self):
        return 'TreeCache'

    def _set_files(self, trees_objects):
        with self.__connection.get_cursor() as datastore:
            inserts = []
            for path, tree in trees_objects.items():
                blob = '\n'.join(self.build_blob(tree))

                name = path.decode('utf8')

                entity = self.__connection.create_entity(self._build_key(datastore, name), exclude_from_indexes=('files', ))

                entity.update({
                    'files': blob.encode('utf8'),
                    'sha': tree.id.decode('utf8'),
                })

                inserts.append(entity)

            datastore.put_multi(inserts)

    def get_commit_id(self):
        with self.__connection.get_cursor() as datastore:
            key = self._build_key(datastore, '')
            entity = datastore.get(key)

            if entity is None:
                return None

            return entity['sha']

    def _get_files(self, scans):
        def name_from_key(entity):
            id_or_name = entity.key.name or entity.key.id
            return b'' if id_or_name == 1 else id_or_name

        with self.__connection.get_cursor() as datastore:
            keys = [self._build_key(datastore, path) for path, _, _ in scans]

            cache_entities = datastore.get_multi(keys)

            return {name_from_key(entity): self._files_sha_array_to_dict(entity['files']) for entity in cache_entities}
