from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class SmsService(Request, OnyxErpService):

    jwt = None
    cache_path = str()

    def __init__(self, base_url: str(), app: object(), cache_root="/tmp/"):
        super(SmsService, self).__init__(app, base_url)
        self.cache_path = cache_root

    def enviar_sms(self, pf_id: str(), telefone: str(), mensagem: str(), remetente="OnyxERP"):
        """
        Envia uma requisição de envio de sms para a SmsAPI
        :rtype: dict | bool
        """
        request = self.set_payload({
            'remetente': remetente,
            'telefone': telefone,
            'mensagem': mensagem,
        }).post("/v2/enviar/%s/" % pf_id)

        status = request.get_status_code()
        response = request.get_decoded()

        if status == 200:
            return True
        else:
            return False

    def get_hash_data(self, hash_name: str(), app_id: str(), lang_id="pt-br"):
        data = self.get_app_meta_data(app_id, lang_id)

        if 'meta' in data and hash_name in data['meta']:
            return data['meta'][hash_name]
        else:
            return False
