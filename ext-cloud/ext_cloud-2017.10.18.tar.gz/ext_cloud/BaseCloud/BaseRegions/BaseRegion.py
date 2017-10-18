from abc import ABCMeta, abstractproperty


class BaseRegioncls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def name(self):
        pass
