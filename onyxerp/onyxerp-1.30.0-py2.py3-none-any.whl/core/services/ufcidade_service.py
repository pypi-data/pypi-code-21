from onyxerp.core.api.request import Request
from onyxerp.core.services.onyxerp_service import OnyxErpService


class UfCidadeService(Request, OnyxErpService):

    jwt = None

    def __init__(self, base_url, app: object()):
        super(UfCidadeService, self).__init__(app, base_url)

    def get_cidade(self, cidade_cod: int()):
        response = self.get("/v1/cidade/{0}/".format(cidade_cod))

        status = response.get_status_code()

        if status == 200:
            return response.get_decoded()
        else:
            return {
                "status": status,
                "response": response.get_content()
            }

    def get_dados_cep(self, cep: str):
        """
        Envia uma requisição GET para a UFCidadeAPI
        :rtype: dict or False
        """
        response = self.get("/v1/cep/%s/" % cep)

        status = response.get_status_code()
        dados = response.get_decoded()

        if status == 200:
            if 'data' in dados and 'entidade_cep' in dados['data']:
                return dados['data']['entidade_cep']
        return False
