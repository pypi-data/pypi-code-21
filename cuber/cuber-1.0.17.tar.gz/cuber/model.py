import abc

class Model(object):
    __metaclass__  = abc.ABCMeta

    @abc.abstractmethod
    def serialise(self):
        return

    @abc.abstractmethod
    def fit(self, **kwargs):
        return

    @abc.abstractmethod
    def predict(self, uid, iid):
        return

    @abc.abstractmethod
    def get_top(self, uid, top_size):
        return

