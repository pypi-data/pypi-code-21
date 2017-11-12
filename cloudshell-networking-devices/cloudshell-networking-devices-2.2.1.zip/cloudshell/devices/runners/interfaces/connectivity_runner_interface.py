from abc import ABCMeta
from abc import abstractmethod


class ConnectivityOperationsInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def apply_connectivity_changes(self, request):
        pass
