import abc


class Generator(object, metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def get():
        pass
