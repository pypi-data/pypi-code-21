from .apps import BaseApp, BaseAppManager
from coreapi.utils import File

import uuid


class InputDataset(BaseApp):
    pass


class InputDatasetManager(BaseAppManager):
    model = InputDataset
    namespace = ['transfer', 'input', 'all']


class FileInput(InputDataset):
    def upload(self, file):
        file.seek(0)
        return self.act(['upload', 'create'], {
            'object_id': self.object_id,
            'file': File(self.object_id, file.read())})


class FileInputManager(InputDatasetManager):
    model = FileInput
    namespace = ['transfer', 'input', 'file', 'all']
    _file = None

    def pre_create(self, **params):
        params['workspace'] = self.workspace.object_id
        params['file'].seek(0)
        params['file'] = File(str(uuid.uuid4()), params['file'].read())
        return params

    def pre_save(self):
        for param in ['workspace']:
            if self._data.get(param, None) is not None and \
                    not isinstance(self._data[param], str):
                self._data[param] = self._data[param].object_id


class CSVInputManager(FileInputManager):
    namespace = ['transfer', 'input', 'file', 'csv']


class WarehouseQueryInputManager(InputDatasetManager):
    namespace = ['transfer', 'input', 'warehouse_query']

    def pre_create(self, **params):
        params['store'] = params['store'].object_id
        params['workspace'] = self.workspace.object_id
        return params

    def pre_save(self):
        for param in ['store', 'workspace']:
            if self._data.get(param, None) is not None and \
                    not isinstance(self._data[param], str):
                self._data[param] = self._data[param].object_id
