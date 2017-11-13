from abc import ABCMeta, abstractproperty


class BaseTenantcls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def status(self):
        pass
