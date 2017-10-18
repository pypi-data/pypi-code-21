# from abc import ABCMeta, abstractmethod, abstractproperty
from abc import ABCMeta, abstractmethod


class BaseTemplatescls:
    __metaclass__ = ABCMeta

    @abstractmethod
    def create_template(self, file=None, data=None, name=None):
        pass

    @abstractmethod
    def get_all_templates(self):
        pass

    @abstractmethod
    def is_valid(self, file=None, data=None):
        pass
