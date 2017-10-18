from abc import ABCMeta, abstractmethod


class BaseIdentitycls:
    __metaclass__ = ABCMeta

    @abstractmethod
    def list_users(self):
        pass

    @abstractmethod
    def list_tenants(self):
        pass
