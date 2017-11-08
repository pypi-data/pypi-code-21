from ks.ks_api.kms_apis.ks_super import KeyServerBase
from ks.settings import mongo_settings

import base64
import hashlib
import os
import string
from secrets import choice

__author__ = "paulq@cisco.com"
__maintainer__ = "Alena Lifar"
__email__ = "alifar@cisco.com"
__copyright__ = "Copyright(c) 2017, Cisco Systems, Inc."
__version__ = "0.4.1"
__status__ = "alpha"


class KsLocal(KeyServerBase):

    @staticmethod
    def generate_secret(nbytes):
        alphabet = string.ascii_letters + string.digits
        secret = ''.join(choice(alphabet) for i in range(nbytes))
        return secret

    def generate_new_key(self, aid: str):
        """
        perform actual key generation: math + db insert

        :param aid: asset id
        :type aid: str

        :return: status and key data
        :rtype: tuple
        """
        collection = mongo_settings.MongoSettings().collection
        key_dict = {}
        k = collection.find_one({"asset_id": aid})
        if k:
            key_dict['cause'] = 'asset already has a key'
            key_dict['success'] = False
            key_dict['asset_id'] = aid
            return False, key_dict
        else:
            # TODO this seems all wrong. Bytes can not be decoded with utf-8 consistently
            key = KsLocal.generate_secret(32)
            #key = os.urandom(32)
            #key_dict['key'] = (base64.b64encode(key).decode('utf-8'))
            key_dict['key'] = key
            key_id = hashlib.sha256(key.encode("utf-8")).hexdigest()
            key_dict['key_server'] = 'local'
            key_dict['use'] = 'asset encryption'
            key_dict['asset_id'] = aid
            key_dict['key_id'] = key_id
            key_dict['state'] = 'active'
            key_dict['iv'] = KsLocal.generate_secret(16)
            # key_dict['iv'] = (base64.b64encode(os.urandom(16)).decode('utf-8'))
            key_dict['algorithm'] = 'AES256'  # TODO: need to add modes and other details
            returned_dict = key_dict.copy()
            dict_to_write = key_dict.copy()
            collection.insert_one(dict_to_write.copy())  # TODO: add error checking on mongo insert or just use RP's core Mongo
            return True, returned_dict

    def get_key_details(self, key_id):
        found_key = super().get_key_details(key_id)
        if not found_key:
            return False, "Key " + key_id + " not found"
        else:
            del found_key['key']
            del found_key['_id']
            return True, found_key

    def construct_requested_key(self, found_k: dict):
        """
        Construct a key dictionary of unified format

        :param found_k: key info
        :type found_k: dict

        :return: status and key details in new format
        :rtype: tuple
        """
        key_to_return = dict(
            key=dict(
                key=found_k['key'],
                key_server=found_k['key_server'],
                asset_id=found_k['asset_id'],
                iv=found_k['iv'],
                ttl=86400,
                algorithm=found_k['algorithm'],
                state=found_k['state'],
                key_id=found_k['key_id']
            )
        )
        return True, key_to_return
