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
This package contains the base class and meta class for all serializable
objects in the Fastr system.
"""

import gzip
import json
import marshal
import os
import pickle
from abc import abstractmethod

from jsonschema.exceptions import ValidationError

import fastr
import fastr.exceptions as exceptions
from fastr.utils import xmltodict, jsonschemaparser


class PassThroughSerializer(object):
    @staticmethod
    def dumps(data):
        return data

    @staticmethod
    def loads(data):
        return data


class Serializable(object):
    """
    Superclass for all classes that can be serialized.
    """
    dumpfuncs = {
        'dict': PassThroughSerializer,
        'json': json,
        'pickle': pickle,
        'marshall': marshal,
        'xml': xmltodict,
    }

    SERIALIZERS = {}

    @classmethod
    def get_serializer(cls, filename=None):
        if filename is None:
            if hasattr(cls, '__dataschemafile__'):
                filename = cls.__dataschemafile__
            else:
                raise exceptions.FastrValueError('Cannot get serializer for class without dataschemafile specified!')
        if not os.path.exists(filename):
            filename = os.path.join(fastr.config.schemadir, filename)

        if filename not in cls.SERIALIZERS:
            try:
                cls.SERIALIZERS[filename] = jsonschemaparser.getblueprinter(filename)
            except IOError as err:
                fastr.log.warning('Serializable class {} cannot read schemafile {}: {}'.format(
                    cls.__name__, filename, err.strerror))

        return cls.SERIALIZERS[filename]

    @abstractmethod
    def __getstate__(self):
        raise exceptions.FastrNotImplementedError('For a Serializable the __getstate__ has to be set by the subjc')

    @classmethod
    def _unserialize(cls, doc, network=None):
        """
        Classmethod that returns an object constructed based on the
        str/dict (or OrderedDict) representing the object

        :param dict doc: the state of the object to create
        :param network: the network the object will belong to
        :type network: :py:class:`Network <fastr.core.network.Network>`
        :return: newly created object
        """
        return cls.createobj(doc, network)

    @classmethod
    def createobj(cls, state, _=None):
        """
        Create object function for generic objects

        :param cls: The class to create
        :param state: The state to use to create the Link
        :param network: the parent Network
        :return: newly created Link
        """
        # Assume a state
        if hasattr(cls, '__base__'):
            # We just check if __base__ existed, but pylint missed that
            # pylint: disable=no-member
            base = cls.__base__
        else:
            raise exceptions.FastrNotImplementedError('Cannot parse old-style classes!')

        if base is object:
            obj = object.__new__(cls)
        else:
            obj = base.__new__(cls)

        if hasattr(obj, '__setstate__'):
            # We just check if __setstate__ existed, but pylint missed that
            # pylint: disable=no-member,maybe-no-member
            obj.__setstate__(state)
        else:
            obj.__dict__.update(state)

        return obj

    def _serialize(self):
        """
        Method that returns a dict/str/list structure with the data to rebuild
        the object.

        :returns: serialized representation of object
        """
        return self.__getstate__()

    def dump(self, file_handle, method='json', **kwargs):
        """
        Dump the object to a file like object.

        :param file_handle: file descriptor to write the data to
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param kwargs: extra arguments passed to the final serializer
        """
        self._dump(self._serialize(), file_handle, method, **kwargs)

    def dumps(self, method='json', **kwargs):
        """
        Dump the object to a string

        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param kwargs: extra arguments passed to the final serializer
        :return: serialization string
        :rtype: str
        """
        return self._dumps(self._serialize(), method, **kwargs)

    def dumpf(self, path, method=None, **kwargs):
        """
        Dump the object to a file

        :param path: path where to write the file
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param kwargs: extra arguments passed to the final serializer

        .. note::
            The dumpf function can determine the method based on the desired
            output filename. Also, if the filename ends with .gz it will
            continue search for another extension (so .json.gz could be found)
            and will then compress the result with gzip.
        """
        self._dumpf(self._serialize(), path, method, **kwargs)

    @classmethod
    def load(cls, file_handle, method=None, network=None, **kwargs):
        """
        Load the object from a file-like object

        :param cls: class of the object
        :param file_handle: file descriptor to write the data to
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param network: network in which to place the loaded object
        :param kwargs: extra arguments passed to the final serializer
        :return: newly created object

        .. warning::
            Unlike the loadf functions, this function does not automatically
            detect gzip compression. You read a gzip using the gzip.open
            method, but not but simply opening a stream and hopeing this
            function will function.
        """
        doc = cls._load(file_handle, method, **kwargs)
        return cls._unserialize(doc, network)

    @classmethod
    def loads(cls, string, method=None, network=None, **kwargs):
        """
        Load the object from a string

        :param cls: class of the object
        :param str string: the string containing the serialized data
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param network: network in which to place the loaded object
        :param kwargs: extra arguments passed to the final serializer
        :return: newly created object
        """
        doc = cls._loads(string, method, **kwargs)
        return cls._unserialize(doc, network)

    @classmethod
    def loadf(cls, path, method=None, network=None, **kwargs):
        """
        Load the object from a file

        :param cls: class of the object
        :param path: path where to write the file
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param network: network in which to place the loaded object
        :param kwargs: extra arguments passed to the final serializer
        :return: newly created object

        .. note::
            The loadf function can determine the method of loading based on the
            filename. Also it can automatically determine whether a file is
            gzipped.
        """
        doc = cls._loadf(path, method, **kwargs)
        obj = cls._unserialize(doc, network)
        obj.filename = path
        return obj

    @classmethod
    def _dump(cls, obj, file_handle, method='json', **kwargs):
        """
        Helper function that calls the dump function of the desired final
        serialized based on the specified method.

        :param cls: class of the object
        :param obj: object to serialize
        :param file_handle: file descriptor to write the data to
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param kwargs: extra arguments passed to the final serializer
        :return: result of the selected ``dump`` function
        """
        if method in cls.dumpfuncs:
            dump_func = cls.dumpfuncs[method].dump
        else:
            message = 'Dump module/class {} not found in _dumpfuns!'.format(method)
            fastr.log.error(message)
            raise exceptions.FastrSerializationMethodError(message)

        return dump_func(obj, file_handle, **kwargs)

    @classmethod
    def _dumps(cls, obj, method='json', **kwargs):
        """
        Helper function that calls the dumps function of the desired final
        serialized based on the specified method.

        :param cls: class of the object
        :param obj: object to serialize
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param kwargs: extra arguments passed to the final serializer
        :return: result of the selected ``dump`` function
        """
        if method in cls.dumpfuncs:
            dumps_func = cls.dumpfuncs[method].dumps
        else:
            message = 'Dump module/class {} not found in _dumpfuns!'.format(method)
            fastr.log.error(message)
            raise exceptions.FastrSerializationMethodError(message)

        return dumps_func(obj, **kwargs)

    @classmethod
    def _dumpf(cls, obj, filename, method=None, **kwargs):
        """
        Helper function that calls the dump function of the desired final
        serialized based on the specified method. Then it writes the result
        to the specified file.

        :param cls: class of the object
        :param obj: object to serialize
        :param path: path where to write the file
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param kwargs: extra arguments passed to the final serializer

        .. note::
            The dumpf function can determine the method based on the desired
            output filename. Also, if the filename ends with .gz it will
            continue search for another extension (so .json.gz could be found)
            and will then compress the result with gzip.
        """
        if filename.endswith('.gz'):
            compress = True
            ext = os.path.splitext(filename[:-3])[1]
        else:
            compress = False
            ext = os.path.splitext(filename)[1]

        if method is None:
            if ext[1:] in cls.dumpfuncs:
                fastr.log.debug('Found extension as viable dump method, selecting {}'.format(ext[1:]))
                method = ext[1:]
            else:
                message = 'Could not determine dump method based on extension ({})'.format(ext)
                fastr.log.error(message)
                raise exceptions.FastrSerializationMethodError(message)

        if compress:
            with gzip.open(filename, 'w') as fout:
                cls._dump(obj, fout, method, **kwargs)
        else:
            with open(filename, 'w') as fout:
                cls._dump(obj, fout, method, **kwargs)

    @classmethod
    def _loads(cls, string, method=None, **kwargs):
        """
        Helper function to select the correct method and load the data from
        a string.

        :param cls: class of object
        :param str string: the string containing the serialized data
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param kwargs: extra arguments passed to the final serializer
        :return: the data loaded from the file

        .. note::
            If no method is given, the function will attempt each known
            loaded and will use the first one that does not raise
            exceptions.
        """
        if method is None:
            # get all available methods, make sure json, pickle and xml are first
            methods = cls.dumpfuncs.keys()
            methods.remove('json')
            methods.remove('pickle')
            methods.remove('xml')
            methods = ['json', 'pickle', 'xml'] + methods

            for method in methods:
                try:
                    doc = cls._loads(string, method, **kwargs)
                    return doc
                except ValidationError:
                    raise
                except (ValueError, KeyError):
                    pass  # Known possible errors with json/pickle/xml parsing
                except Exception:
                    raise

            raise exceptions.FastrSerializationMethodError('Could not load string, no suitable reader found')

        if method in cls.dumpfuncs:
            loads_func = cls.dumpfuncs[method].loads
        else:
            message = 'Dump module/class not found in _dumpfuns!'
            fastr.log.error(message)
            raise exceptions.FastrSerializationMethodError(message)

        doc = loads_func(string, **kwargs)
        if hasattr(cls, '__dataschemafile__'):
            # We just check if __dataschemafile__ existed, but pylint missed that
            # pylint: disable=no-member
            doc = cls.get_serializer().instantiate(doc)

        return doc

    @classmethod
    def _load(cls, file_object, method=None, **kwargs):
        """
        Helper function to select the correct method and load the data from
        a file-like object.

        :param cls: class of object
        :param file_object: file descriptor to write the data to
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param kwargs: extra arguments passed to the final serializer
        :return: the data loaded from the file

        .. warning::
            Unlike the loadf functions, this function does not automatically
            detect gzip compression. You read a gzip using the gzip.open
            method, but not but simply opening a stream and hopeing this
            function will function.
        """
        return cls._loads(file_object.read(), method, **kwargs)

    @classmethod
    def _loadf(cls, path, method=None, **kwargs):
        """
        Helper function to select the correct method and load the data from
        a file.

        :param cls: class of object
        :param path: path of the file to load
        :param str method: method of final serialization to use
                           (e.g. json, xml, pickle)
        :param kwargs: extra arguments passed to the final serializer
        :return: the data loaded from the file

        .. note::
            The loadf function can determine the method of loading based on the
            filename.  Also it can automatically determine whether a file is
            gzipped.
        """
        # Try to guess the method based on the extension
        if method is None:
            # get all available methods, make sure json, pickle and xml are first
            methods = cls.dumpfuncs.keys()

            for potential_method in methods:
                if path.endswith('.{}'.format(method)) or path.endswith('.{}.gz'.format(method)):
                    method = potential_method
                    break

        if not os.path.isfile(path):
            message = 'File not found ({})'.format(path)
            fastr.log.error(message)
            raise exceptions.FastrIOError(message)

        # Try if the file is GZipped
        try:
            with gzip.open(path, 'r') as fin:
                data = cls._load(fin, method, **kwargs)
                return data
        except IOError:
            pass

        # Treat as uncompressed file
        try:
            with open(path, 'r') as fin:
                data = cls._load(fin, method, **kwargs)
        except ValueError:
            #raise exceptions.FastrSerializationMethodError('Load failed! Could not find a suitable reader for {}.'.format(path))
            raise

        return data

    @classmethod
    def _unicode_convert(cls, input_):
        """
        Helper function to convert unicode instances in a data structure to str

        :param cls: class of object
        :param input_: the data structure to convert
        :return: converted version of the data
        """
        if isinstance(input_, dict):
            return {cls._unicode_convert(key): cls._unicode_convert(value) for key, value in input_.iteritems()}
        elif isinstance(input_, list):
            return [cls._unicode_convert(element) for element in input_]
        elif isinstance(input_, unicode):
            return input_.encode('utf-8')
        else:
            return input_
