from abc import ABCMeta, abstractmethod


class SnmpHandlerInterface(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_snmp_service(self):
        pass
