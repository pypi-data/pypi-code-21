from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class MetaService(Request, OnyxErpService):

    jwt = None
    cache_path = str()

    def __init__(self, base_url: str(), app: object(), cache_root="/tmp/"):
        super(MetaService, self).__init__(app, base_url)
        self.cache_path = cache_root

    def get_app_meta_data(self, app_id: str(), lang_id="pt-br"):
        """
        Recupera informações da MetaAPI
        :rtype: dict | bool
        """
        if lang_id is False:
            end_point = "/v1/data/%s/" % (app_id)
        else:
            end_point = "/v1/data/%s/%s/" % (app_id, lang_id)

        request = self.get(end_point)

        status = request.get_status_code()
        response = request.get_decoded()

        if status == 200:
            return response['data']['MetaAPI']
        else:
            return False

    def get_hash_data(self, hash_name: str(), app_id: str(), lang_id="pt-br"):
        data = self.get_app_meta_data(app_id, lang_id)

        if 'meta' in data and hash_name in data['meta']:
            return data['meta'][hash_name]
        else:
            return False
