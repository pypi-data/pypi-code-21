from abc import abstractmethod

__all__ = ["AbstractScript"]


class AbstractScript(object):
    def __init__(self, manager):
        self.manager = manager

    @abstractmethod
    def main(self):
        pass
