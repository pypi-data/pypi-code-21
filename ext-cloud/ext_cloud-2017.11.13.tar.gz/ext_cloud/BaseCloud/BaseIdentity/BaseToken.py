from abc import ABCMeta, abstractproperty


class BaseTokencls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def username(self):
        pass

    @abstractproperty
    def tenant_name(self):
        pass

    @abstractproperty
    def auth_url(self):
        pass
