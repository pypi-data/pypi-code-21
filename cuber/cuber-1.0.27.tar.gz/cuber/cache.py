import logging
import copy

logger = logging.getLogger(__name__)

# https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
class Singleton(object):
    _instance = None
    def __new__(class_, *args, **kwargs):
        if not isinstance(class_._instance, class_):
            class_._instance = object.__new__(class_, *args, **kwargs)
        return class_._instance

class Cache(Singleton, object):
    '''
    cache dict: key (cache) -> {'value': cached_value, another system info}
    TODO: add immutable promise (that'll allow not to copy the item)
    '''
    def __init__(self):
        if 'cache' not in self.__dict__:
            self.cache = {}
            logger.info('Cache resetted: {}'.format(id(self.cache)))

    def get(self, key, do_not_copy = False):
        '''
            Returns pair (status, value).
            Status: bool. Is true, if key is stored
        '''
        if key in self.cache:
            if do_not_copy:
                return (True, self.cache.get(key).get('value'))
            else:
                return (True, copy.deepcopy(self.cache.get(key).get('value')))
        else:
            return (False, None)

    def add(self, key, value, do_not_copy = False):
        if do_not_copy:
            self.cache[key] = {
                'value': value
            }
        else:
            self.cache[key] = {
                'value': copy.deepcopy(value)
            }

