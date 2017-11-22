from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class GovService(Request, OnyxErpService):

    """
    Service responsável por interfacear o acesso HTTP de outras APIs do OnyxERP à GovAPI
    """
    jwt = None
    cache_service = object

    def __init__(self, base_url, app: object(), cache_root="/tmp/"):
        super(GovService, self).__init__(app, base_url)
        self.cache_service = CacheService(cache_root, "GovAPI")

    def get_lotacao(self, lotacao_id: str()):
        """
        Acessa o end-point em GovAPI responsável pela listagem das informações de uma lotaçõa, de acordo com a
        documentação em https://goo.gl/HF3YPG
        :param lotacao_id: str
        :return: dict
        """
        cached_data = self.cache_service.get_cached_data('lotacao', lotacao_id)

        if cached_data:
            return self.deserialize_cached_model('lotacao_id', cached_data)

        response = self.get("/v1/lotacao/%s/" % lotacao_id)

        status = response.get_status_code()
        data = response.get_decoded()['data']

        if status == 200:
            return data['GovernancaAPI']
        else:
            return False

    def get_cargo(self, cargo_id: str()):
        """
        Acessa o end-point em GovAPI responsável pela listagem das informações de um cargo, de acordo com a documentação
        em https://goo.gl/NUoYzw
        :param cargo_id: str
        :return: dict
        """
        cached_data = self.cache_service.get_cached_data('cargo', cargo_id)

        if cached_data:
            return self.deserialize_cached_model('cargo_id', cached_data)

        response = self.get("/v1/cargo/%s/" % cargo_id)

        status = response.get_status_code()
        data = response.get_decoded()['data']

        if status == 200:
            return data['GovernancaAPI']
        else:
            return False
