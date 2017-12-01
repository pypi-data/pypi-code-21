from .StorageStrategy import StorageStrategy

class LocalStorage(StorageStrategy):
    def _read(self, path):
        content = None
        with open(path, 'r') as src:
            content = src.read()
        return content
