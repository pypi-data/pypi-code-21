import json
from collections import OrderedDict

# Compat between Python 3.4 and Python 3.5
if not hasattr(json, 'JSONDecodeError'):
    json.JSONDecodeError = ValueError
from json import JSONDecodeError

import requests

from evosnap.data_element_encoder import DataElementEncoder
from evosnap.exceptions import TransactionRequestException
from evosnap.response import Response
from evosnap.service_information.mixins import ServiceInformationRequestMixin
from evosnap.transactions.enum import RequestType


class TransactionRequestMixin(ServiceInformationRequestMixin):
    def __init__(self, **kwargs):
        """
        Basic information about the check being processed. This element is Required.
        :param activation: Contains information for activating an account. This is a required element.
        """
        self.cws_tps_baseurl=kwargs.get('cws_tps_baseurl')

        self.data = kwargs.get('data', '')
        self.workflow_id=kwargs.get('workflow_id', '')
        self.batch_ids=kwargs.get('batch_ids')
        self.transaction_ids=kwargs.get('transaction_ids')
        self.force_close=kwargs.get('force_close')
        super(TransactionRequestMixin, self).__init__(**kwargs)

    @property
    def __authorize_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.authorize.value),
            ('ApplicationProfileId', self.application_profile_id),
            ('MerchantProfileId', self.merchant_profile_id),
            ('Transaction', self.data),
        ]), cls=DataElementEncoder)

    @property
    def __authorize_and_capture_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.authorize_and_capture.value),
            ('ApplicationProfileId', self.application_profile_id),
            ('MerchantProfileId', self.merchant_profile_id),
            ('Transaction', self.data),
        ]), cls=DataElementEncoder)

    @property
    def __manage_account_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.manage_account.value),
            ('ApplicationProfileId', self.application_profile_id),
            ('MerchantProfileId', self.merchant_profile_id),
            ('Transaction', self.data),
        ]), cls=DataElementEncoder)

    @property
    def __adjust_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.adjust.value),
            ('ApplicationProfileId', self.application_profile_id),
            ('DifferenceData', self.data),
        ]), cls=DataElementEncoder)

    @property
    def __undo_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.undo.value),
            # ('sessionToken', None),
            ('differenceData', self.data),
            ('applicationProfileId', self.application_profile_id),
        ]), cls=DataElementEncoder)

    @property
    def __capture_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.capture.value),
            ('ApplicationProfileId', self.application_profile_id),
            ('DifferenceData', self.data),
        ]), cls=DataElementEncoder)

    @property
    def __resubmit_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.resubmit.value),
            ('ApplicationProfileId', self.application_profile_id),
            ('MerchantProfileId', self.merchant_profile_id),
            ('Transaction', self.data),
        ]), cls=DataElementEncoder)

    @property
    def __capture_selective_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.capture_selective.value),
            ('ApplicationProfileId', self.application_profile_id),
            ('DifferenceData', self.data),
            ('TransactionIds', self.transaction_ids),
        ]), cls=DataElementEncoder)

    @property
    def __capture_all_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.capture_all.value),
            ('ApplicationProfileId', self.application_profile_id),
            ('MerchantProfileId', self.merchant_profile_id),
            ('DifferenceData', self.data),
            ('BatchIds', self.batch_ids),
            ('ForceClose', self.force_close)
        ]), cls=DataElementEncoder)

    @property
    def __return_by_id_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.return_by_id.value),
            ('ApplicationProfileId', self.application_profile_id),
            ('MerchantProfileId', self.merchant_profile_id),
            ('DifferenceData', self.data),
        ]), cls=DataElementEncoder)

    @property
    def __return_unlinked_json(self):
        return json.dumps(OrderedDict([
            ('$type', RequestType.return_unlinked.value),
            ('ApplicationProfileId', self.application_profile_id),
            ('MerchantProfileId', self.merchant_profile_id),
            ('Transaction', self.data),
        ]), cls=DataElementEncoder)
        # return json.dumps(OrderedDict([
        #     ('$type', RequestType.return_unlinked.value),
        #     # ('ApplicationProfileId', self.application_profile_id),
        #     # ('MerchantProfileId', self.merchant_profile_id),
        #     # ('Transaction', self.data),
        # ]), cls=DataElementEncoder)

    @property
    def request_json(self):
        if self.request_type == RequestType.authorize:
            return self.__authorize_json
        elif self.request_type == RequestType.authorize_and_capture:
            return self.__authorize_and_capture_json
        elif self.request_type == RequestType.manage_account:
            return self.__manage_account_json
        elif self.request_type == RequestType.adjust:
            return self.__adjust_json
        elif self.request_type == RequestType.undo:
            return self.__undo_json
        elif self.request_type == RequestType.capture:
            return self.__capture_json
        elif self.request_type == RequestType.resubmit:
            return self.__resubmit_json
        elif self.request_type == RequestType.capture_selective:
            return self.__capture_selective_json
        elif self.request_type == RequestType.capture_all:
            return self.__capture_all_json
        elif self.request_type == RequestType.return_by_id:
            return self.__return_by_id_json
        elif self.request_type == RequestType.return_unlinked:
            return self.__return_unlinked_json

    @property
    def request_endpoint(self):
        if self.request_type == RequestType.authorize:
            return self.cws_tps_baseurl+'/'+self.workflow_id
        elif self.request_type == RequestType.authorize_and_capture:
            return self.cws_tps_baseurl+'/'+self.workflow_id
        elif self.request_type == RequestType.manage_account:
            return self.cws_tps_baseurl+'/'+self.workflow_id
        elif self.request_type == RequestType.adjust:
            return self.cws_tps_baseurl+'/'+self.workflow_id+'/'+self.data.transaction_id
        elif self.request_type == RequestType.undo:
            return self.cws_tps_baseurl+'/'+self.workflow_id+'/'+self.data.transaction_id
        elif self.request_type == RequestType.capture:
            return self.cws_tps_baseurl+'/'+self.workflow_id+'/'+self.data.transaction_id
        elif self.request_type == RequestType.resubmit:
            return self.cws_tps_baseurl+'/'+self.workflow_id
        elif self.request_type == RequestType.capture_selective:
            return self.cws_tps_baseurl+'/'+self.workflow_id
        elif self.request_type == RequestType.capture_all:
            return self.cws_tps_baseurl+'/'+self.workflow_id
        elif self.request_type == RequestType.return_by_id:
            return self.cws_tps_baseurl+'/'+self.workflow_id
        elif self.request_type == RequestType.return_unlinked:
            return self.cws_tps_baseurl+'/'+self.workflow_id

    @property
    def request_method(self):
        if self.request_type in [RequestType.adjust, RequestType.undo, RequestType.capture]:
            return 'PUT'
        else:
            return 'POST'

    def send(self, test_request=None):
        self.sign_on()
        # print(self.request_endpoint)
        response = requests.request(
            method=self.request_method,
            url=self.request_endpoint,
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            data=self.request_json if not test_request else json.dumps(test_request),
            auth=(self.session_token, ''),
            verify=self.ssl_verification
        )
        if response.status_code!=200 and response.status_code!=201 and response.status_code!=400:
            try:
                msg = str(response.status_code)+' '+Response(response.text).to_pretty_json()
                # print(response.request.body)
                # print(response.headers)
                # print(response.request.headers)
                raise TransactionRequestException(msg)
            except JSONDecodeError:
                msg = str(response.status_code) + ' ' + response.text
                # print(response.headers)
                # print(response.headers)
                raise TransactionRequestException(msg)
        return Response(response.text)
