import json
from json import JSONDecodeError
from time import time

import requests

from evosnap import constants
from evosnap.exceptions import SignOnException, AppProfileException
from evosnap.transactions.enum import RequestType

class ServiceInformationRequestMixin:
    def __init__(self, **kwargs):
        """
        Basic information about the check being processed. This element is Required.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.ssl_verification=kwargs.get('ssl_verification')

        self.cws_sis_baseurl=kwargs.get('cws_sis_baseurl')
        self.cws_tms_baseurl=kwargs.get('cws_tms_baseurl')

        self.identity_token=kwargs.get('identity_token')
        self.session_token=kwargs.get('session_token')
        self.session_token_time=kwargs.get('session_token_time')

        self.service_key=kwargs.get('service_key')
        self.username=kwargs.get('username')
        self.password=kwargs.get('password')
        self.new_password=kwargs.get('new_password')
        self.new_username=kwargs.get('new_username')
        self.new_email=kwargs.get('new_email')

        self.request_type=kwargs.get('request_type')

        self.application_profile_id=kwargs.get('application_profile_id')
        self.service_id=kwargs.get('service_id')
        self.merchant_profile_id=kwargs.get('merchant_profile_id')
        super(ServiceInformationRequestMixin, self).__init__()

    def is_signed_on(self):
        return self.session_token and time()-self.session_token_time <= constants.SESSION_TOKEN_TIME

    def sign_on(self):
        if not self.is_signed_on():
            response = requests.get(
                url=self.cws_sis_baseurl+'/token',
                auth=(self.identity_token,''),
                headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
                verify=self.ssl_verification
            )
            if response.status_code == 200:
                self.session_token_time = time()
                print(response.text)
                self.session_token = json.loads(response.text)
            else:
                raise SignOnException(response.text)

    def app_profile(self):
        self.sign_on()
        response = requests.get(
            url=self.cws_sis_baseurl+'/appProfile/'+self.application_profile_id,
            auth=(self.session_token, ''),
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            verify=self.ssl_verification
        )
        if response.status_code == 200:
            return json.dumps(json.loads(response.text), indent=4, sort_keys=True)
        else:
            try:
                msg = str(response.status_code)+' '+json.dumps(json.loads(response.text), indent=4, sort_keys=True)
                raise AppProfileException(msg)
            except JSONDecodeError:
                raise AppProfileException(str(response.status_code)+' '+response.text)

