import importlib
import os
import random
import shutil
import types
import uuid
from typing import Tuple, Dict

import requests


class IdGenerator(object):
    def generate(self) -> str:
        return str(uuid.uuid4())


class ModuleImporter(object):
    def import_module(self, module_name: str) -> types.ModuleType:
        return importlib.import_module(module_name)


class StdoutWriter(object):
    def write(self, *args):
        print(*args)


class NoOpStdoutWriter(StdoutWriter):
    def write(self, *args):
        pass


class RandomGenerator(object):
    def choice(self, seq):
        return random.choice(seq)


HttpClientResponse = Tuple[int, str, Dict[str, str], str]


class HttpClient(object):
    def request(self, method, url, headers, body) -> HttpClientResponse:
        response = requests.request(method, url, headers=headers, data=body)
        return response.status_code, response.reason, response.headers, response.text


class FileSystem(object):
    def is_file(self, path):
        return os.path.isfile(path)

    def create_directory(self, dir):
        os.makedirs(dir, exist_ok=True)

    def append_to_file(self, path, content):
        with open(path, 'a') as fh:
            fh.write(content)

    def copy_file(self, source, destination):
        shutil.copyfile(source, destination)

    def read_file(self, path) -> str:
        with open(path) as fh:
            return fh.read()
