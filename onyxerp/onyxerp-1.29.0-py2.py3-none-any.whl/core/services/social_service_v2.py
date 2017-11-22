from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class SocialServiceV2(Request, OnyxErpService):
    """
    Serviço responsável pela interação de APIs do OnyxERP com a SocialAPI-v2
    """
    jwt = None
    cache_service = object

    def __init__(self, base_url, app: object(), cache_root="/tmp/"):
        super(SocialServiceV2, self).__init__(app, base_url)
        self.cache_service = CacheService(cache_root, "SocialAPI")

    def inserir_pf(self):
        """
        Cadastra uma pessoa física em SocialAPI
        """
        response = self.post("/v1/pessoa-fisica/")

        status = response.get_status_code()
        dados = response.get_decoded()

        if status == 201:
            return dados['data']['SocialAPI']
        else:
            return False

    def inserir_pf_foto(self, pf_id: str) -> bool:
        """
        Cadastra uma foto para uma pessoa física em SocialAPI
        :param pf_id: str
        :rtype bool
        """
        response = self.post("/v1/pessoa-fisica/foto/%s/" % pf_id)

        status = response.get_status_code()

        if status == 201:
            return True
        else:
            return False

    def get_pf_perfil(self, pf_id: str()):
        """
        Busca uma pessoa física pela id em SocialAPI
        :param pf_id: str
        :return: dict | False
        """
        cached_data = self.cache_service.get_cached_data('pessoa', pf_id)
        if cached_data:
            return cached_data

        response = self.get("/v1/pessoa-fisica/perfil/%s/" % str(pf_id))

        status = response.get_status_code()
        dados = response.get_decoded()

        if status == 200:
            pf_data = dados['data']['SocialAPI']

            self.cache_service.write_cache_data('pessoa', pf_id, pf_data)

            return pf_data
        else:
            return False
