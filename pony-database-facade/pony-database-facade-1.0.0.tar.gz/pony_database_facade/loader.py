# coding: utf-8
#
# Copyright 2017 Kirill Vercetti
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import ABCMeta, abstractmethod
import sys

import six

if six.PY34:
    import importlib.util
else:
    import imp


__all__ = ('Loader',)


class BaseLoader(six.with_metaclass(ABCMeta)):
    __slots__ = ()

    __counter = 0

    @classmethod
    def _create_module_name(cls, name):
        cls.__counter += 1
        return '{}_10{}'.format(name, cls.__counter)

    @abstractmethod
    def load(self, name):
        pass

    def load_and_registry(self, name):
        mod = self.load(name)
        sys.modules[self._create_module_name(name)] = mod
        return mod


class ImpLoader(BaseLoader):
    __slots__ = ()

    def load(self, name):
        file = None
        path = None

        try:
            if name.find('.', 1) != -1:
                parent, name = name.split('.', 1)
                parent = self.load(parent)
                path = getattr(parent, '__path__', None)

            file, pathname, description = imp.find_module(name, path)
            mod = imp.load_module(self._create_module_name(name), file, pathname, description)
            return mod
        finally:
            if file:
                file.close()


class ImportLibLoader(BaseLoader):
    __slots__ = ()

    def load(self, name):
        spec = None

        try:
            spec = importlib.util.find_spec(name)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
        finally:
            del spec


Loader = ImportLibLoader if six.PY34 else ImpLoader
