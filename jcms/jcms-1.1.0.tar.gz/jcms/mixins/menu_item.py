from abc import ABCMeta, abstractmethod


class MenuItem(object):
    __metaclass__ = ABCMeta

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    @abstractmethod
    def slug(self):
        pass

    @property
    @abstractmethod
    def items(self):
        pass
