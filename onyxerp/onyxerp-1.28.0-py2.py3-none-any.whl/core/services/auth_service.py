from onyxerp.core.api.request import Request
from onyxerp.core.services.onyxerp_service import OnyxErpService


class AuthService(Request, OnyxErpService):

    jwt = None

    def __init__(self, base_url, app: object()):
        super(AuthService, self).__init__(app, base_url)

    def auth(self):
        response = self.post("/v1/auth/")

        status = response.get_status_code()
        data = response.get_decoded()

        if status == 200 or status == 401:
            return data['access_token']
        else:
            return {
                "status": status,
                "response": response.get_content()
            }
