from abc import ABCMeta, abstractproperty


class BaseImagecls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def size(self):
        pass

    @abstractproperty
    def state(self):
        pass
