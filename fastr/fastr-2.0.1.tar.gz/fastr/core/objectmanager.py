# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
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

"""
This module contains the object manager class
"""

from abc import abstractproperty, abstractmethod

import fastr
from fastr.core.basemanager import BaseManager
from fastr.core.version import Version
import fastr.exceptions as exceptions


class ObjectManager(BaseManager):
    """
    Class for managing all the objects loaded in the fastr system
    """
    def __init__(self, path):
        """
        Create a ObjectManager and scan path to search for Objects

        :param path: the path(s) to scan for Objects
        :type path: str or iterable of str
        :return: newly created ObjectManager
        """
        super(ObjectManager, self).__init__(path, True)

    def __contains__(self, key):
        """
        Check if an item is in the ObjectManager

        :param key: object id or tuple (Objectid, version)
        :type key: str or tuple
        :return: flag indicating the item is in the manager
        """
        return self.__keytransform__(key) in self.data

    def __getitem__(self, key):
        """
        Retrieve a Object from the ObjectManager. You can request by only an id,
        which results in the newest version of the Object being returned, or
        request using both an id and a version.

        :param key: object id or tuple (Objectid, version)
        :type key: str or tuple
        :return: the requested Object
        :raises FastrObjectUnknownError: if a non-existing Object was requested
        """
        new_key = self.__keytransform__(key)
        if new_key not in self.data:
            raise exceptions.FastrObjectUnknownError('Key "{}" (expanded to {}) not found in {}'.format(key, new_key, type(self).__name__))

        obj = self.data[new_key]
        return obj

    def __keytransform__(self, key):
        """
        Key transform, used for allowing indexing both by id-only and by
        ``(id, version)``

        :param key: key to transform
        :return: key in form ``(id, version)``
        """
        # Get the version (or None)
        if isinstance(key, (str, unicode)):
            namespace, object_id, version = None, key, None
        elif isinstance(key, tuple):
            if len(key) == 2:
                object_id, version = key
                namespace = None
            elif len(key) == 3:
                namespace, object_id, version = key
            else:
                raise exceptions.FastrValueError('Object key in tuple form should be length 2 or 3, '
                                                 'in the form (id, version) or (namespace, id, version)'
                                                 'found {}'.format(key))
        else:
            raise exceptions.FastrTypeError('Object key should be a string, unicode or tuple!')

        # Split out version first (it may contain./, whereas namespace and object won't contain /)
        if version is None and '/' in object_id:
            object_id, version = object_id.split('/', 1)

        # Split out namespace
        if namespace is None and '.' in object_id:
            namespace, object_id = object_id.rsplit('.', 1)

        if isinstance(version, (str, unicode)):
            version = Version(version)

        # Check that we are done (should be unique match)
        if all(x is not None for x in [namespace, object_id, version]):
            return namespace, object_id, version

        # Check the namespace, if there is only 1 namespace with a object, use that
        if namespace is None:
            namespaces = {k[0] for k in self.keys() if k[1] == object_id}

            if len(namespaces) == 0:
                return namespace, object_id, version
            elif len(namespaces) > 1:
                raise exceptions.FastrValueError('Multiple versions of Object {} found in different namespaces,'.format(object_id) +
                                                 ' need to pick an explicit namespace! (namespace: {})'.format(sorted(namespaces)))

            namespace = namespaces.pop()

        # If the version is not given, figure it out using newest version available
        if version is None:
            versions = [k[2] for k in self.keys() if k[0] == namespace and k[1] == object_id]

            if len(versions) > 0:
                version = max(versions)

        return namespace, object_id, version

    @property
    def _item_extension(self):
        """
        Extension of files to load
        """
        return '(xml|json)'

    @abstractproperty
    def object_class(self):
        """
        The class of the objects to populate the manager with
        """

    @abstractmethod
    def get_object_version(self, obj):
        """
        Get the version of a given object

        :param object: the object to use
        :return: the version of the object
        """

    def _print_key(self, key):
        """
        Print function for the keys
        """
        object_id = key[0] if key[0] else ''
        if object_id != '':
            object_id += '.'
        object_id += key[1]
        return (object_id, 'v{}'.format(str(key[2])))

    def _print_value(self, value):
        """
        Print function for the values
        """
        return value.filename

    def _load_item(self, filepath, namespace):
        """
        Load a Object file and store it in the Manager
        """
        obj = self.object_class.loadf(filepath)
        object_version = self.get_object_version(obj)

        # Make sure the last part of the directory structure is not the version
        # if that is the case, strip it
        if len(namespace) > 0:
            possible_version = namespace[-1]

            try:
                possible_version = Version(possible_version)
                if possible_version == object_version:
                    namespace = namespace[:-1]
            except exceptions.FastrVersionInvalidError:
                pass

        namespace = '.'.join(namespace)
        self._store_item((namespace, obj.id, object_version), obj)
        obj.namespace = namespace

    def todict(self):
        """
        Return a dictionary version of the Manager

        :return: manager as a dict
        """
        result = {}
        for key in self.keys():
            if key[0] not in result:
                result[key[0]] = []

            if str(key[1]) not in result[key[0]]:
                result[key[0]].append(str(key[1]))

        return result

    def objectversions(self, obj):
        """
        Return a list of available versions for the object

        :param object: The object to check the versions for. Can be either a `Object` or a `str`.
        :return: List of version objects. Returns `None` when the given object is not known.
        """

        if isinstance(obj, self.object_class):
            objectname = obj.id
            namespace = obj.namespace
        else:
            try:
                obj = self[obj]
                objectname = obj.id
                namespace = obj.namespace
            except exceptions.FastrObjectUnknownError as e:
                fastr.log.error("Error requesting object versions: Object ({}) is not known.".format(obj))
                return None
        fastr.log.info("objectname: {}".format(objectname))
        return sorted(key[2] for key in self.keys() if key[0] == namespace and key[1] == objectname)
