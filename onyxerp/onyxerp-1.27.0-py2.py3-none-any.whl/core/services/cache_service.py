import os
import json
from collections import OrderedDict

from django.utils import timezone


class CacheService(object):
    cache_path = str()
    cache_root = str()

    def __init__(self, cache_root="", cache_path=""):
        self.cache_root = cache_root
        self.cache_path = cache_path

    def get_cached_data(self, cache_name, cache_file_id):
        cache_file = "%s/%s/json/%s/%s.json" % (self.cache_root, self.cache_path, cache_name, cache_file_id)

        if os.path.isfile(cache_file):
            return self.read_file(cache_file)
        else:
            return False

    def write_cache_data_pf(self, pf_id: str(), oid: str(), cache_name: str(), data: dict()):
        cache_dir = "%s/%s/json/%s/%s/%s" % (
            self.cache_root, self.cache_path, pf_id, cache_name, oid
        )

        if os.path.isdir(cache_dir) is False:
            self.build_cache_path(pf_id, cache_name, oid)

        file_timestamp = timezone.now().timestamp()
        return self.write_file_raw("%s/%s.json" % (cache_dir, str(file_timestamp).replace('.', '')), data)

    def write_cache_data_inverso(self, oid: str(), ref_id: str(), file_id: str(), cache_name: str(), data: dict()):
        cache_dir = "%s/%s/json/%s/%s" % (
            self.cache_root, self.cache_path, cache_name, oid
        )

        if os.path.isdir(cache_dir) is False:
            os.mkdir(cache_dir, 0o777)

        cache_ref_dir = "%s/%s" % (cache_dir, ref_id)

        if os.path.isdir(cache_ref_dir) is False:
            os.mkdir(cache_ref_dir, 0o777)

        file_name = "%s/%s.json" % (cache_ref_dir, file_id)
        return self.write_file_raw(file_name, data)

    def build_cache_path(self, pf_id: str(), cache_name: str(), oid: str()):
        pf_path = "%s/%s/json/%s" % (self.cache_root, self.cache_path, pf_id)

        if os.path.isdir(pf_path) is False:
            os.mkdir(pf_path, 0o777)

        cache_pf_path = "%s/%s" % (pf_path, cache_name)

        if os.path.isdir(cache_pf_path) is False:
            os.mkdir(cache_pf_path, 0o777)

        cache_pf_oid_path = "%s/%s/%s" % (pf_path, cache_name, oid)

        if os.path.isdir(cache_pf_oid_path) is False:
            os.mkdir(cache_pf_oid_path, 0o777)

        return True

    def write_cache_data(self, cache_name, cache_file_id, data):
        cache_file = "%s/%s/json/%s/%s.json" % (self.cache_root, self.cache_path, cache_name, cache_file_id)
        return self.write_file(cache_file, data)

    def remove_cached_data(self, cache_name, cache_file_id):
        cache_file = "%s/%s/json/%s/%s.json" % (self.cache_root, self.cache_path, cache_name, cache_file_id)
        return self.remove_file(cache_file)

    @staticmethod
    def read_file_raw(file_name):
        if os.path.isfile(file_name):
            handle = open(file_name, "r")
            json_data = handle.read()
            handle.close()
            return json_data
        else:
            return False

    @staticmethod
    def write_file_raw(file_name, data):
        handle = open(file_name, "w+")
        handle.write(data)
        handle.close()
        return True

    @staticmethod
    def read_file(file_name):
        if os.path.isfile(file_name):
            json_data = False
            handle = open(file_name, "r")
            data = handle.read()
            if len(data) > 0:
                json_data = json.loads(data, object_pairs_hook=OrderedDict)
            handle.close()
            return json_data
        else:
            return False

    @staticmethod
    def write_file(file_name, data):
        handle = open(file_name, "w+")
        handle.write(json.dumps(data))
        handle.close()
        return True

    @staticmethod
    def remove_file(file_name):
        if os.path.isfile(file_name):
            os.unlink(file_name)
            return True
        else:
            return False
