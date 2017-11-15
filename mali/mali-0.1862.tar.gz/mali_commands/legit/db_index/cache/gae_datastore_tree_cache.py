# coding=utf-8
import binascii
import cPickle as pickle
import stat
import math
import zlib
from ...gae_datastore_mixin import GAEDatastoreMixin
from .tree_cache import TreeCache
from google.appengine.ext import ndb


class TreeCacheModel(ndb.Model):
    files_part = ndb.BlobProperty(required=True)
    sha = ndb.StringProperty(required=True)
    data_splits = ndb.IntegerProperty(required=True)
    volume_id = ndb.IntegerProperty()  # This is a new prop its needs to be required but for backward support it can't

    @classmethod
    def _get_kind(cls):
        return 'TreeCache'

    @property
    def name(self):
        entity_id = self.key.id()
        return '' if entity_id == 1 else entity_id

    @classmethod
    def key_with_data_part(cls, key, data_part):
        name = key.id()

        if data_part > 0:
            name = '%s:%s' % (name, data_part)

        return ndb.Key(cls, name, parent=key.parent(), namespace=key.namespace())

    @property
    def shred_keys(self):
        if self.data_splits == 1:
            return []

        return [self.key_with_data_part(self.key, part) for part in range(1, self.data_splits)]


class GAEDatastoreTreeCache(GAEDatastoreMixin, TreeCache):
    MAX_SHRED_SIZE = 1024 * 1024 - (10 * 1024)

    def __init__(self, org_id, volume_id):
        super(GAEDatastoreTreeCache, self).__init__(org_id, volume_id)

    def delete_all(self):
        self.delete_all_by_class(TreeCacheModel)

    @property
    def _entity_kind(self):
        return 'TreeCache'

    @classmethod
    def build_blob(cls, tree):
        for item in tree.iteritems():
            is_dir = item.mode & stat.S_IFDIR == stat.S_IFDIR
            yield (item.path.decode('utf8'), binascii.unhexlify(item.sha.decode('utf8')), is_dir)

    def _set_files(self, trees_objects):
        inserts = []
        for path, tree in trees_objects.items():
            name = path.decode('utf8')

            data_dump = pickle.dumps(list(self.build_blob(tree)), pickle.HIGHEST_PROTOCOL)

            data = zlib.compress(data_dump)

            data_splits = int(math.ceil(len(data) / float(self.MAX_SHRED_SIZE)))

            start_index = 0
            for part in range(data_splits):
                end_index = min(start_index + self.MAX_SHRED_SIZE, len(data))

                entity = TreeCacheModel(
                    key=TreeCacheModel.key_with_data_part(self._build_key(name), part),
                    data_splits=data_splits,
                    files_part=data[start_index:end_index],
                    volume_id=self._volume_id,
                    sha=tree.id.decode('utf8'))

                inserts.append(entity)

                start_index += self.MAX_SHRED_SIZE

        ndb.put_multi(inserts)

    def get_commit_id(self):
        entity = self._build_key('').get()

        if entity is None:
            return None

        return entity.sha

    @classmethod
    def _files_sha_array_to_dict(cls, files):
        result = {}
        for name, sha, is_dir in files:
            result[name] = (binascii.hexlify(sha), stat.S_IFDIR if is_dir else 0)

        return result

    @classmethod
    def __open_files_parts(cls, files_parts):
        one_big_string = ''
        for shred_entity in files_parts:
            if shred_entity is None:
                return None

            one_big_string += shred_entity.files_part

        return pickle.loads(zlib.decompress(one_big_string))

    @classmethod
    def __get_entities_and_shared(cls, keys):
        cache_entities = [entity for entity in ndb.get_multi(keys) if entity is not None]

        shared_keys = []
        for entity in cache_entities:
            shared_keys.extend(entity.shred_keys)

        shared_cache_entities = ndb.get_multi(shared_keys)

        return cache_entities, shared_cache_entities

    def _get_files(self, scans):
        keys = [self._build_key(path) for path, _, _ in scans]

        cache_entities, shared_cache_entities = self.__get_entities_and_shared(keys)

        files = {}
        shards_index = 0
        for entity in cache_entities:
            files_parts = [entity]
            files_parts.extend(shared_cache_entities[shards_index:shards_index + entity.data_splits - 1])
            shards_index += entity.data_splits
            files_data = self.__open_files_parts(files_parts)

            if files_data is not None:
                files[entity.name] = files_data

        return {name: self._files_sha_array_to_dict(data) for name, data in files.items()}
