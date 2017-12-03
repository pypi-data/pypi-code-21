import json
import os
import tempfile
import shutil
import trust
from abc import ABCMeta
from .logged_tests import LoggedTests


class CommonTests(LoggedTests, metaclass=ABCMeta):
    def setUp(self):
        super().setUp()
        self._temp_path = tempfile.mkdtemp(prefix="createvm-test-trust")

    def tearDown(self):
        shutil.rmtree(self._temp_path)

    @property
    def _finder(self):
        return trust.FileFinder(data_path=self._temp_path)

    def _writeJson(self, path, obj):
        full_path = os.path.join(self._temp_path, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w") as f:
            json.dump(obj, f)
            self._logger.debug("Wrote the JSON file %s.", full_path)
