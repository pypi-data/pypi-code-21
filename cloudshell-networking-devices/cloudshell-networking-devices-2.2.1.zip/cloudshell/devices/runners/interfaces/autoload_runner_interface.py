from abc import ABCMeta
from abc import abstractmethod


class AutoloadOperationsInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def discover(self):
        pass
