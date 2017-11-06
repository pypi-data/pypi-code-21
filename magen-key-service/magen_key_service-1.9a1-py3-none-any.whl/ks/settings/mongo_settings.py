from magen_utils_apis.singleton_meta import Singleton
from pymongo import MongoClient

__author__ = "paulq@cisco.com"
__maintainer__ = "Alena Lifar"
__email__ = "alifar@cisco.com"
__copyright__ = "Copyright(c) 2017, Cisco Systems, Inc."
__version__ = "0.4.1"
__status__ = "alpha"

collection_name = 'key_data'
db_name = 'key_db'


class MongoSettings(metaclass=Singleton):
    def __init__(self, mip=None, mport=None):
        self.mip = mip
        self.mport = mport
        if not self.mip or not self.mport:
            raise ValueError("Can't instantiate MongoClient without host and port")
        self.client = MongoClient(mip, mport)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def drop_db(self):
        self.db.drop_collection(collection_name)
