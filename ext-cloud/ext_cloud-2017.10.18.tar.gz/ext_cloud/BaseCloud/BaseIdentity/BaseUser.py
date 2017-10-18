from abc import ABCMeta, abstractproperty


class BaseUsercls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def email_id(self):
        pass

    @abstractproperty
    def status(self):
        pass
