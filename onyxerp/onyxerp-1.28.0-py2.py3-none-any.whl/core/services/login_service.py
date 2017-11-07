from onyxerp.core.api.request import Request
from onyxerp.core.services.onyxerp_service import OnyxErpService


class LoginService(Request, OnyxErpService):
    jwt = None

    def __init__(self, base_url, app: object()):
        super(LoginService, self).__init__(app, base_url)

    def login(self):
        response = self.post("/v2/login/")

        status = response.get_status_code()
        data = response.get_decoded()

        if status == 200:
            return data['access_token']
        else:
            return {
                "status": status,
                "response": response.get_content()
            }
