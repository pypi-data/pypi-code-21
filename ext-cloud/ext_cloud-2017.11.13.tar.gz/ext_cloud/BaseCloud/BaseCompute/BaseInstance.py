from abc import ABCMeta, abstractmethod, abstractproperty

from enum import Enum


class STATE(Enum):
    UNKNOWN = 0,
    STARTING = 1,
    RUNNING = 2,
    PAUSED = 3,
    STOPPED = 4,
    STOPPING = 5,
    REBOOTING = 6,
    TERMINATED = 7,
    ERROR = 8


class BaseInstancecls:
    __metaclass__ = ABCMeta

    @property
    def resource_type(self):
        return 'instance'

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def size(self):
        pass

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def public_ip(self):
        pass

    @abstractproperty
    def state(self):
        pass

    @abstractproperty
    def image_id(self):
        pass

    @abstractproperty
    def image_name(self):
        pass

    @abstractproperty
    def arch(self):
        pass

    @abstractproperty
    def network_id(self):
        pass

    @abstractproperty
    def subnet_id(self):
        pass

    @abstractproperty
    def private_ip(self):
        pass

    @abstractproperty
    def keypair_name(self):
        pass

    @abstractproperty
    def dns_name(self):
        pass

    @abstractproperty
    def creation_time(self):
        pass

    @abstractproperty
    def os_type(self):
        pass

    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def reboot(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def addtag(self, name=None, value=None):
        pass

    @abstractmethod
    def gettags(self):
        pass
