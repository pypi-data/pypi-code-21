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
This module manages datatypes. These datatypes are python classes generated
from the XML/JSON datatype files.
"""
import os
import xml.etree.ElementTree as ElementTree

import fastr
import fastr.datatypes
from fastr.core.pluginmanager import BasePluginManager
from fastr.core.version import Version
from fastr.data import url
from fastr.datatypes import BaseDataType, DataType, TypeGroup, EnumType, Deferred
import fastr.exceptions as exceptions
from fastr.utils.checksum import hashsum


class DataTypeManager(BasePluginManager):
    """
    The DataTypeManager hold a mapping of all DataTypes in the fast system and
    can create new DataTypes from files/data structures.
    """

    def __init__(self):
        """
        The DataTypeManager constructor will create a new DataTypeManager and
        populate it with all DataTypes it can find in the paths set in
        ``fastr.config.types_path``.

        :return: the created DataTypeManager
        """
        self.types_map = {}
        super(DataTypeManager, self).__init__(fastr.config.types_path)

    @property
    def preferred_types(self):
        return [self.data[t] for t in fastr.config.preferred_types if t in self.data]

    @property
    def fullid(self):
        """
        The fullid of the datatype manager
        """
        return 'fastr://typelist'

    @property
    def plugin_class(self):
        """
        The PluginClass of the items of the BasePluginManager
        """
        return BaseDataType

    # Allow key to be a id string or DataType
    def __keytransform__(self, key):
        """
        Key transformation for this mapping. The key transformation allows
        indexing by both the DataType name as well as the DataType it self.

        :param key: The name of the requested datatype or the datatype itself
        :type key: fastr.datatypes.BaseDataType or str
        :return: The requested datatype
        """
        if self.isdatatype(key):
            if key.name in self.data and self.data[key.name] is key:
                return key.name
            else:
                raise exceptions.FastrDataTypeMismatchError('key DataType {} not {}'.format(key.name, type(self).__name__))
        else:
            return key

    def populate(self):
        """
        Populate Manager. After scanning for DataTypes, create the AnyType and set the preferred types
        """
        super(DataTypeManager, self).populate()

        # Add the any type
        self['AnyType'] = fastr.datatypes.AnyType
        self['AnyFile'] = fastr.datatypes.AnyFile
        self['Deferred'] = fastr.datatypes.Deferred

    @property
    def _instantiate(self):
        """
        Flag indicating that the plugin should NOT be instantiated prior to saving
        """
        return False

    def _print_key(self, key):
        if key.startswith('__') and key.endswith('__'):
            return None

        return key

    def has_type(self, name):
        """
        Check if the datatype with requested name exists

        :param str name: the name of the requested datatype
        :return: flag indicating if the datatype exists
        :rtype: bool
        """
        return name in self.data

    def poll_datatype(self, filename):
        """
        Poll an xml file to see if there is a definition of a datatype in it.

        :param str filename: path of the file to poll
        :return: tuple with (id, version, basetype) if a datatype is found or (None, None, None) if no datatype is found
        """
        if os.path.exists(filename):
            tree = ElementTree.parse(filename)
            root = tree.getroot()

            if root.tag not in ('type', 'typegroup'):
                message = 'Invalid root tag ({}) in file!'.format(root.tag)
                fastr.log.warning(message)
                return (None, None, None)

            id_ = root.get('id')
            version = Version(root.get('version'))

            return (id_, version, root.tag)
        else:
            message = '{} not a valid filename'.format(filename)
            fastr.log.warning(message)
            return (None, None, None)

    def get_type(self, name):
        """Read a type given a typename. This will scan all directories in
        types_path and attempt to load the newest version of the DataType.

        :param str name: Name of the datatype that should be imported in the system
        :return: the datatype with the requested name, or None if datatype is not found

        .. note:: If type is already in TypeManager it will not load anything and return the
                  already loaded version.
        """
        fastr.log.debug('Attemping to get datatype {}'.format(name))
        if name in self:
            return self[name]

        latest_version = Version('0.0')
        latest_filename = ''

        for path in fastr.config.types_path:
            filename = os.path.join(path, name + '.xml')
            if os.path.exists(filename):
                (pollname, version, _) = self.poll_datatype(filename)
                if pollname == name and version > latest_version:
                    latest_version = version
                    latest_filename = filename

        if latest_filename == '':
            message = 'Could not find type with name {}'.format(name)
            fastr.log.error(message)
            return None

        fastr.log.debug('Found {} (version {}) in {}'.format(name, latest_version, latest_filename))
        self._load_item(latest_filename)
        return self[name]

    def _store_item(self, name, value):
        """
        Store an item in the BaseManager, will ignore the item if the key is
        already present in the BaseManager.

        :param name: the key of the item to save
        :param value: the value of the item to save
        :return: None
        """
        super(DataTypeManager, self)._store_item(name, value)

        if value.id is not None:
            value.__module__ = 'fastr.datatypes'
            setattr(fastr.datatypes, value.id, value)

    def create_enumtype(self, type_id, options, name=None):
        """
        Create a python class based on an XML file. This function return a
        completely functional python class based on the contents of a DataType
        XML file.

        Such a class will be of type EnumType.

        :param str type_id: the id of the new class
        :param iterable options: an iterable of options, each option should be str
        :return: the newly created subclass of EnumType
        :raises FastrTypeError: if the options is not an iterable of str
        """
        if type_id in self:
            if self[type_id].options != set(options):
                raise exceptions.FastrDataTypeMismatchError('Conflicting definition of Enum {}!'
                                                            ' (options {} vs {})'.format(type_id,
                                                                                         self[type_id].options,
                                                                                         options))

            fastr.log.debug('Returning existing DataType {}!'.format(type_id))
            return self[type_id]

        attributes = {}

        try:
            if isinstance(options, str):
                options = (options,)

            attributes['_options'] = frozenset(options)
        except TypeError:
            message = 'options must be a iterable containing the valid options for the Enum, found options {}'.format(options)
            fastr.log.error(message)
            raise exceptions.FastrTypeError(message)

        if not all(isinstance(x, str) for x in attributes['_options']):
            message = 'all options for an Enum must be of type str, found options {}'.format(options)
            fastr.log.error(message)
            raise exceptions.FastrTypeError(message)

        attributes['parent'] = self
        attributes['_sourcepath'] = None
        attributes['_hash'] = hashsum([type_id, name, options])
        attributes['__module__'] = 'fastr.datatypes'

        supertypes = (EnumType,)

        fastr.log.debug('Creating EnumType {} from script'.format(type_id))
        out = type(type_id, supertypes, attributes)
        self[type_id] = out
        setattr(fastr.datatypes, out.id, out)
        return out

    def guess_type(self, value, exists=True, options=None, preferred=None):
        """
        Guess the DataType based on a value str.

        :param str value: the value to guess the type for
        :param options: The options that are allowed to be guessed from
        :type options: TypeGroup, DataType or tuple of DataTypes
        :param bool extists: Indicate the value exists (if file) and can be
                             checked for validity, if false skip validity check
        :param iterable preferred: An iterable of preferred types in case
                                   multiple types match.
        :return: The resulting DataType or None if no match was found
        :raises FastrTypeError: if the options argument is of the wrong type

        The function will first create a list of all candidate DataTypes.
        Subsequently, it will check for each candidate if the value would
        valid. If there are multiple matches, the config value for preferred
        types is consulted to break the ties. If non of the DataTypes are in
        the preferred types list, a somewhat random DataType will be picked
        as the most optimal result.
        """
        fastr.log.debug('Guesstype value: {}, options: {}, preferred: {}'.format(value, options, preferred))
        if options is None:
            options = set([x for x in self.values() if issubclass(x, DataType)])
        elif issubclass(options, TypeGroup):
            options = set(options.members)
        elif issubclass(options, DataType):
            options = set((options,))
        elif isinstance(options, tuple):
            options = set(options)
        else:
            raise exceptions.FastrTypeError('Invalid type for options ({})'.format(options))

        fastr.log.debug('Guesstype options: {}'.format(options))
        candidates = set()

        scheme = None
        if url.isurl(value):
            scheme = url.get_url_scheme(value)
            if scheme != 'vfs':
                if scheme != 'val':
                    fastr.log.warning('Cannot determine DataType based on URL with scheme {}'.format(url.get_url_scheme(value)))
                    return None

        for option in options:
            if not issubclass(option, DataType):
                continue
            elif issubclass(option, Deferred):
                continue  # We never want to find a deferred (it is not a valid type for an instance)
            elif option.extension is None:
                candidates.add(option)
            elif isinstance(value, (str, unicode)) and value.endswith('.{}'.format(option.extension)):
                candidates.add(option)

        fastr.log.debug('Guesstype candidates: {}'.format(candidates))
        if len(candidates) == 0:
            fastr.log.debug('No valid combinations of options and candidates!')
            return None

        if len(candidates) != 1 and exists:
            # Test validity of value for each DataType
            final_candidates = []
            for candidate in candidates:
                temp = candidate(value)
                if temp.valid:
                    final_candidates.append(candidate)
        else:
            final_candidates = list(candidates)

        # Remove types in these order in case of mutliple matches, that means
        # the Int has precidence over the Boolean, Float and String in case
        # of a tie
        types_to_remove = ['String', 'Float', 'Boolean', 'Int', 'UnsignedInt']

        fastr.log.debug('Final candidates: {}'.format(final_candidates))

        if len(final_candidates) > 1:
            for type_to_remove in types_to_remove:
                if fastr.typelist[type_to_remove] in final_candidates:
                    final_candidates.remove(fastr.typelist[type_to_remove])
                if len(final_candidates) == 1:
                    break

        if len(final_candidates) == 0:
            return None
        elif len(final_candidates) == 1:
            fastr.log.debug('Matched a single type: {}'.format(final_candidates[0]))
            return final_candidates[0]
        else:
            fastr.log.debug('Multiple DataTypes match, trying to find a preferred match! Remaining candidates: {}'.format(final_candidates))

            # Get preferred types from argument list
            if preferred is not None:
                for type_ in preferred:
                    if type_ in final_candidates:
                        fastr.log.info('Found preferred match (from keyword): {}'.format(type_))
                        return type_

            # Get preferred information from the config
            for type_ in self.preferred_types:
                if type_ in final_candidates:
                    fastr.log.debug('Found preferred match: {}'.format(type_))
                    return type_

        fastr.log.debug('Mutliple matches, removing matches without extension')
        backup_candidate = final_candidates[0]
        final_candidates = [x for x in final_candidates if x.extension is not None]

        if len(final_candidates) == 1:
            return final_candidates[0]
        else:
            if len(final_candidates) > 1:
                fastr.log.error('Multiple DataTypes match, but no preferred match, picking one at random! Remaining candidates: {}'.format(final_candidates))
                return final_candidates[0]
            else:
                fastr.log.error('No final DataTypes match value "{}", using the backup type: {}'.format(value,
                                                                                                        backup_candidate))
                return backup_candidate

    def match_types(self, *args, **kwargs):
        """
        Find the match between a list of DataTypes/TypeGroups, see :ref:`resolve-datatype` for details

        :param args: A list of DataType/TypeGroup objects to match
        :param kwargs: A 'preferred' keyword argument can be used to indicate a list of DataTypes to prefer in case of ties (first has precedence over later in list)
        :return: The best DataType match, or None if no match is possible.
        :raises FastrTypeError: if not all args are subclasses of BaseDataType
        """
        options = self.match_types_any(*args)

        # Check if it is a preferred type
        if 'preferred' in kwargs and kwargs['preferred'] is not None:
            if not all([self.isdatatype(item) for item in kwargs['preferred']]):
                message = 'All preferred types must be DataTypes!'
                fastr.log.warning(message)

            preferred = kwargs['preferred']
        else:
            preferred = self.preferred_types

        if len(options) == 0:
            fastr.log.warning("No matching DataType available (args {})".format(args))
            return None
        elif len(options) == 1:
            # This is a perfect match, no preferences needed
            result = options.pop()

            return result
        else:
            # Get preferred information from the config
            for type_ in preferred:
                if type_ in options:
                    return type_

            fastr.log.debug("No preferred DataType matches, (options {}, preferred {})".format(options, preferred))
            return None

    def match_types_any(self, *args):
        """
        Find the match between a list of DataTypes/TypeGroups, see :ref:`resolve-datatype` for details

        :param args: A list of DataType/TypeGroup objects to match
        :return: A set with all DataTypes that match.
        :rtype: set
        :raises FastrTypeError: if not all args are subclasses of BaseDataType
        """
        # Find a single argument that is a list
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]

        # Remove typeless str
        args = tuple(arg for arg in args if arg != str)

        if not all([self.isdatatype(item) for item in args]):
            message = 'All arguments must be DataTypes! (Found {})'.format(args)
            fastr.log.error(message)
            raise exceptions.FastrTypeError(message)

        # In case there are no args
        if len(args) == 0:
            fastr.log.debug("No DataTypes given to match")
            return None

        # Create an initial options set (make sure to copy and not reference the set!)
        if issubclass(args[0], TypeGroup):
            options = set(args[0].members)
        else:
            options = set((args[0],))

        # Find intersection of all arguments
        for datatype in args[1:]:
            if isinstance(datatype, DataType):
                datatype = type(datatype)

            if issubclass(datatype, TypeGroup):
                options &= datatype.members
            else:
                options &= set((datatype,))

        return options

    @staticmethod
    def isdatatype(item):
        """
        Check if item is a valid datatype for the fastr system.

        :param item: item to check
        :return: flag indicating if the item is a fastr datatype
        :rtype: bool
        """
        return isinstance(item, (type, type)) and issubclass(item, BaseDataType)


if 'typelist' not in locals():
    typelist = DataTypeManager()
