import json
from abc import ABC, abstractmethod

class DBModelMixin(object):  
    def __str__(self):
        return json.dumps(self.__dict__)

    def to_json(self):
        return json.dumps(self.__dict__)

    def to_dict(self):
        return self.__dict__

class BaseDB(ABC, DBModelMixin):
    @abstractmethod
    def add(self, item):
        pass
        
    @abstractmethod
    def add_batch(self, items):
        pass
        
    @abstractmethod
    def get(self, key, value):
        pass
        
    @abstractmethod
    def get_all(self, filter_key=None, filter_value=None, partial_match=False):
        pass

    @abstractmethod
    def update(self, key, value, update_key, update_value):
        pass

    @abstractmethod
    def delete(self, key, value):
        pass

    @abstractmethod
    def purge(self):
        pass
