from abc import abstractmethod

__all__ = ["AbstractScript"]


class AbstractScript(object):
    def __init__(self, manager):
        self.manager = manager
        self.settings = manager.settings
        self.app = manager.application

    @abstractmethod
    def main(self):
        pass
