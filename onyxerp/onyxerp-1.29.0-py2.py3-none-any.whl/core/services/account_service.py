from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class AccountService(Request, OnyxErpService):

    """

    """
    jwt = None
    cache_service = object

    def __init__(self, base_url, app: object(), cache_root="/tmp/"):
        super(AccountService, self).__init__(app, base_url)
        self.cache_service = CacheService(cache_root, "AccountAPI")

    def get_usuario(self, uuid: str()):
        """

        :param uuid:
        :return:
        """
        cached_data = self.cache_service.get_cached_data('usuario', uuid)

        if cached_data:
            return cached_data

        response = self.get("/v1/usuario/%s/" % uuid)

        status = response.get_status_code()

        if status == 200:
            data = response.get_decoded()['data']
            self.cache_service.write_cache_data('usuario', uuid, data['AccountAPI'])
            return data['AccountAPI']
        else:
            return False

    def get_usuario_by_cod(self, usuario_cod: int()):
        """

        :param usuario_cod:
        :return:
        """
        cached_data = self.cache_service.get_cached_data('usuario', usuario_cod)

        if cached_data:
            return cached_data

        response = self.get("/v1/usuario/cod/{0}/".format(usuario_cod))

        status = response.get_status_code()

        if status == 200:
            data = response.get_decoded()['data']
            self.cache_service.write_cache_data('usuario', usuario_cod, data['AccountAPI'])
            return data['AccountAPI']
        else:
            return False
