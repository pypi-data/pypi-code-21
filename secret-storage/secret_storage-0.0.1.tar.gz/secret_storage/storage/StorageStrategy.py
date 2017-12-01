from abc import ABC, abstractmethod


class StorageStrategy(ABC):

    def __init__(self):
        self._cache = {}

    def read(self, path):
        if path not in self._cache:
            content = self._read(path)
            self._cache[path] = content
        return self._cache[path]

    @abstractmethod
    def _read(self, path):
        pass
