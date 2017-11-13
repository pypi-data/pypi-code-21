from abc import ABCMeta, abstractmethod, abstractproperty


class BaseKeycls:
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        pass

    @abstractproperty
    def oid(self):
        pass

    @abstractproperty
    def size(self):
        pass

    @abstractmethod
    def delete(self):
        pass

    @abstractmethod
    def download(self, file_path):
        pass

    @abstractmethod
    def upload(self, file_path):
        pass

    @abstractmethod
    def get_url(self):
        pass
