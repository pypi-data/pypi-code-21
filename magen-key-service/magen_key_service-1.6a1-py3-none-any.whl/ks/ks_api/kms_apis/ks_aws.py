from json import JSONDecodeError

from ks.ks_api.kms_apis.ks_super import KeyServerBase
from ks.settings import mongo_settings

import base64
import hashlib
import logging
import os
import json

import boto3
from magen_logger.logger_config import LogDefaults


__author__ = "paulq@cisco.com"
__maintainer__ = "Alena Lifar"
__email__ = "alifar@cisco.com"
__copyright__ = "Copyright(c) 2017, Cisco Systems, Inc."
__version__ = "0.4.1"
__status__ = "alpha"


DEFAULT_TTL = 86400


def read_config(file_name: str, magen_logger=None):
    """
    Reads and formats config file

    :param file_name: name of config file or path
    :param magen_logger: magen logger

    :return: data from config
    :rtype: dict
    """
    logger = magen_logger or logging.getLogger(LogDefaults.default_log_name)
    dir_name = os.path.dirname(os.path.abspath(__file__))
    path = '{0}/{1}'.format(dir_name, file_name)
    try:
        with open(path) as f:
            print(f)
            return json.loads(f.read())
    except FileNotFoundError as e:
        logger.error(e)
        raise
    except JSONDecodeError as e:
        logger.error('Cannot read from empty file: ', e)
        raise


class KsAws(KeyServerBase):

    _instance = None

    def __init__(self, magen_logger):
        """
        init the local class with requisite Mongo details

        :param magen_logger: logger object that was initialized before
        :type magen_logger: logger
        """
        self.logger = magen_logger
        self.aws_config = read_config('aws_config.json', self.logger)
        self.cmkID = self.aws_config.get('cmk_id', None)
        self.algo = self.aws_config.get('keyspec', None)
        self.aws_client = boto3.client(
            'kms',
            region_name=self.aws_config.get('region_name', None),
            aws_access_key_id=self.aws_config.get('aws_access_key_id', None),
            aws_secret_access_key=self.aws_config.get('aws_secret_access_key', None)
        )

    def get_aws_key(self):
        """
        Generate AWS key based on config

        :return: encrypted key
        :rtype: bytes
        """
        encrypted_key_blob = self.aws_client.generate_data_key(KeyId=self.aws_config.get('cmk_id', None),
                                                               KeySpec=self.aws_config.get('keyspec', None))
        return encrypted_key_blob['CiphertextBlob']

    def decrypt_aws_key(self, k: bytes):
        """
        Perform a decryption on a given key

        :param k: key
        :type k: bytes

        :return: decrypted key
        :rtype: bytes
        """
        r = self.aws_client.decrypt(CiphertextBlob=k)
        return r['Plaintext']

    def generate_new_key(self, asset_id: str):
        """
        perform actual key generation: math + db insert

        :param asset_id: asset id
        :type asset_id: str

        :return: status and generated key info
        :rtype: tuple
        """
        key_dict = {}
        collection = mongo_settings.MongoSettings().collection
        k = collection.find_one({"asset_id": asset_id})
        if k:
            key_dict['cause'] = 'asset already has a key'
            key_dict['success'] = False
            key_dict['asset_id'] = asset_id
            return False, key_dict
        else:
            aws_key_encrypted = self.get_aws_key()
            key_id = hashlib.sha256(aws_key_encrypted).hexdigest()
            key_dict['encrypted_binary_key'] = aws_key_encrypted
            key_dict['encrypted_key'] = (base64.b64encode(aws_key_encrypted).decode('utf-8'))
            key_dict['key'] = (base64.b64encode(self.decrypt_aws_key(aws_key_encrypted)).decode('utf-8'))
            key_dict['key_server'] = 'awskms'
            key_dict['use'] = 'asset encryption'
            key_dict['asset_id'] = asset_id
            key_dict['key_id'] = key_id
            key_dict['state'] = 'active'
            key_dict['iv'] = (base64.b64encode(os.urandom(16)).decode('utf-8'))
            key_dict['algorithm'] = 'AES256'  #TODO: need to add modes and other details
            returned_dict = key_dict.copy()
            dict_to_write = key_dict.copy()
            del returned_dict['encrypted_key']
            del returned_dict['encrypted_binary_key']
            del dict_to_write['key']
            collection.insert_one(dict_to_write.copy())  #TODO: add error checking on mongo insert or just use RP's core Mongo
            return True, returned_dict

    def get_key_details(self, key_id):
        found_key = super().get_key_details(key_id)
        if not found_key:
            return False, "Key " + key_id + " not found"
        else:
            del found_key['encrypted_binary_key']
            del found_key['encrypted_key']
            del found_key['_id']
            return True, found_key

    def construct_requested_key(self, found_k: dict):
        """
        Construct a key dictionary without pushing it to db

        :param found_k: key information
        :type found_k: dict

        :return: status and update key info
        :rtype: tuple
        """
        key_to_return = dict(
            key=dict(
                key=base64.b64encode(self.decrypt_aws_key(found_k['encrypted_binary_key'])),
                key_server=found_k['key_server'],
                asset_id=found_k['asset_id'],
                iv=found_k['iv'],
                ttl=DEFAULT_TTL,
                algorithm=found_k['algorithm'],
                state=found_k['state'],
                key_id=found_k['key_id']
            )
        )
        return True, key_to_return

    @classmethod
    def get_instance(cls, magen_logger=None):
        if not cls._instance:
            cls._instance = cls(magen_logger or logging.getLogger(LogDefaults.default_log_name))
        return cls._instance
