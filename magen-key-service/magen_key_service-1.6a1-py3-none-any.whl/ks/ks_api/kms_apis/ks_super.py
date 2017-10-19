from ks.settings import mongo_settings
from abc import ABCMeta, abstractmethod

__author__ = "paulq@cisco.com"
__maintainer__ = "Alena Lifar"
__email__ = "alifar@cisco.com"
__copyright__ = "Copyright(c) 2017, Cisco Systems, Inc."
__version__ = "0.4.1"
__status__ = "alpha"


class KeyServerBase(metaclass=ABCMeta):
    """
    Base class for different types of key server connection
    """

    __instance = None

    @abstractmethod
    def generate_new_key(self, asset_id: str):
        pass

    @staticmethod
    def rm_key(key_id: str):
        """
        Delete key by updating flag 'state'

        :param key_id: key id
        :type key_id: str

        :return:  status and message
        :rtype: tuple
        """
        collection = mongo_settings.MongoSettings().collection
        result = collection.update_one({'key_id': key_id},
                                       {
                                           '$set': {
                                               'state': 'deleted'
                                           }
                                       }
                                       )
        if result.matched_count == 1:
            msg = {key_id: 'state --> deleted'}
            return True, msg
        else:
            msg = {"error": key_id + " not deleted"}
            return False, msg

    def get_key_details(self, key_id):
        """
        Request detailed key information

        :param key_id:
        :return: key data
        :rtype: dict
        """
        collection = mongo_settings.MongoSettings().collection
        found_key = collection.find_one({"key_id": key_id})
        return found_key

    @staticmethod
    def state_change(key_id, state):
        collection = mongo_settings.MongoSettings().collection
        if state == 0:
            active = 'deactive'
        else:
            active = 'active'
        r = collection.update_one({'key_id': key_id},
                                  {
                                      '$set': {
                                          'state': active
                                      }
                                  }
                                  )
        if r.matched_count == 1:
            msg = {key_id: 'state ' + active}
            success = True
        else:
            msg = {"error": key_id + " not updated"}
            success = False
        return success, msg

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = cls()
        return cls.__instance
