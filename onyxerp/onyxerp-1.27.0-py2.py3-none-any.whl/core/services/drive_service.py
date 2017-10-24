import hashlib
import json

from onyxerp.core.api.request import Request
from onyxerp.core.services.onyxerp_service import OnyxErpService


class DriveService(Request, OnyxErpService):

    jwt = None

    def __init__(self, base_url, app: object()):
        super(DriveService, self).__init__(app, base_url)

    def get_stored_files(self, ref_cod: int(), app_mod_cod: int()):
        end_point = "/v1/{0}/modulo/{1}/".format(ref_cod, app_mod_cod)

        response = self.get(end_point)

        status = response.get_status_code()

        if status == 200:
            return response.get_decoded()
        else:
            return False

    def get_pf_docs(self, ref_id: str()):
        end_point = "/v2/docs/%s/" % ref_id

        response = self.get(end_point)

        status = response.get_status_code()

        if status == 200:
            return response.get_decoded()
        else:
            return False

    def upload_file_sync(self, ref_cod, app_mod_cod):
        response = self.post("/v1/{0}/modulo/{1}/".format(ref_cod, app_mod_cod))

        status = response.get_status_code()

        if status == 200:
            return response.get_decoded()
        else:
            return {
                "status": status,
                "response": response.get_content()
            }

    def upload_files(self, ref_cod, app_mod_cod):
        response = self.post("/v1/{0}/modulo/{1}/".format(ref_cod, app_mod_cod))

        status = response.get_status_code()

        if status == 200:
            return True
        else:
            return {
                "status": status,
                "response": response.get_content()
            }

    def upload_promise(self, ref_id: str(), files: list(), device_data: dict()):
        str_files = json.dumps(files)
        response = self.set_payload({
            "files": files,
            "checksum": hashlib.sha256(str_files.encode("utf-8")).hexdigest(),
            "device": device_data
        }).post("/v2/upload/%s/" % ref_id)

        status = response.get_status_code()

        if status == 202:
            dados = response.get_decoded()
            return dados['data']['StorageAPI']
        else:
            return False
