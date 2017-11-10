import adal
import requests
import json
from . import constants as const
from . import classes as C

import logging
log = logging.getLogger()

class PowerBI(object):
    def __init__(self, user_name, password, client_id):
        self._user_name, self._password, self._client_id  = \
             user_name, password, client_id

        self._aad_token = None
        self._is_connected = False

    def connect(self):
        context = adal.AuthenticationContext(
                    const.PBI_AUTHORITY,
                    validate_authority=True,
                    api_version=None)

        token_response = context.acquire_token_with_username_password(
                                 const.PBI_RESOURCE,
                                 self._user_name,
                                 self._password,
                                 self._client_id)

        self._aad_token = token_response["accessToken"]
        self._is_connected = True
    def request(self, req):
        '''
        sends a request to PBI Service. It must be formed beforehand
        '''
        headers = {"Authorization": "Bearer " + self._aad_token}

        log.debug(req)

        response = requests.get(req, headers=headers)
        resp = json.loads(response.text)

        log.debug(response.text)

        if "error" in resp:
            raise RuntimeError("Site returned error: " + str(resp))
        return json.loads(response.text)["value"]
    def get_workspaces(self):
        """
        returns workspaces(groups) as iterator of tuples (id, name)
        """
        groups =  self.request(const.GROUPS_LIST)
        ret = []

        #return default workspace (My workspace)
        ret.append( C.Workspace(self))

        for g in groups:
            ret.append( C.Workspace(self, g["id"], g["name"], g["isReadOnly"]))

        return ret