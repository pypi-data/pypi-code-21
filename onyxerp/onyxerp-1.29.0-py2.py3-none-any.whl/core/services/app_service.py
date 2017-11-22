import base64
import os

from onyxerp.core.api.request import Request
from onyxerp.core.services.cache_service import CacheService
from onyxerp.core.services.onyxerp_service import OnyxErpService


class AppService(Request, OnyxErpService):

    jwt = None
    __cache_path = str()

    def __init__(self, config: dict(), app: object()):
        super(AppService, self).__init__(app, config["URL_APP_API"])
        self.__cache_path = config['CACHE_PATH']

    def get_app(self, app_id):

        file_name = "{0}/AppAPI/apps/{1}.json" .format(
            self.__cache_path, base64.decodebytes(app_id.encode("utf-8")).decode("utf-8")
        )

        if os.path.isfile(file_name):
            return CacheService.read_file(file_name)

        response = self.get("/v1/app/{0}/".format(app_id))

        status = response.get_status_code()
        data = response.get_decoded()

        if status == 200:
            CacheService.write_file(file_name, data)
            return data
        else:
            return {
                "status": status,
                "response": response.get_content()
            }
