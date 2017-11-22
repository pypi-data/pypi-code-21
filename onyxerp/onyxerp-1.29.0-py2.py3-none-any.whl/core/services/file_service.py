import os

from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class FileService(Request, OnyxErpService):

    jwt = None
    cache_service = object()
    cache_path = str()

    def __init__(self, base_url: str(), app: object(), cache_root="/tmp/"):
        super(FileService, self).__init__(app, base_url)
        self.cache_service = CacheService(cache_root, "StorageAPI")
        self.cache_path = cache_root

    def get_file_info(self, ref_id: str(), oid: str(), file_id: str()):
        """
        Recupera as informações de um arquivo armazenado na StorageAPI, se possível, a partir do cache, caso contrário
        envia uma requisição GET e então builda o cache.
        :rtype: dict | bool
        """
        file_name = "%s/StorageAPI/json/docs/%s/%s/%s.json"  % (self.cache_path, oid, ref_id, file_id)

        if os.path.isfile(file_name):
            return self.cache_service.read_file(file_name)

        request = self.get("/v2/doc/%s/%s/" % (ref_id, file_id))

        status = request.get_status_code()
        response = request.get_decoded()

        if status == 200:
            self.build_doc_cache_path(ref_id, oid)
            self.cache_service.write_file(file_name, response['data']['StorageAPI'])
            return response['data']['StorageAPI']
        else:
            return False

    def build_doc_cache_path(self, ref_id: str(), oid: str()):
        """
        Monta o path do cache de um arquivo da StorageAPI criando as pastas, caso estas ainda não existam
        :rtype: str
        """
        cache_oid_dir = "%s/StorageAPI/json/docs/%s" % (self.cache_service.cache_root, oid)

        if os.path.isdir(cache_oid_dir) is False:
            os.mkdir(cache_oid_dir, 0o777)

        cache_dir = "%s/%s" % (cache_oid_dir, ref_id)

        if os.path.isdir(cache_dir) is False:
            os.mkdir(cache_dir, 0o777)

        return cache_dir
