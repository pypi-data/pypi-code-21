from smartbotsol import BaseState
# TODO Try add descriptor for memcache 
class User(object):
    def __init__(self, uid):
        self.uid = uid
        self.state = None
        self.lang = 'ru'

    def __hash__(self):
        return hash(self.uid)

    def __eq__(self, other):
        if self.uid == other.uid:
            return True
        return False

    def __str__(self):
        return 'User[uid: {}; state: {}; lang: {}]'.format(self.uid, self.state, self.lang)

    def to_dict(self):
        data = dict()

        for key in iter(self.__dict__):

            value = self.__dict__[key]
            
            if isinstance(value, BaseState):
                value = value.__class__.__name__

            if value is not None:
                if hasattr(value, 'to_dict'):
                    data[key] = value.to_dict()
                else:
                    data[key] = value

        return data        
