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
This module contains the Manager class for Plugins in the fastr system
"""

import collections
import imp
import inspect
import os
import sys
import traceback
from abc import abstractproperty
from types import ModuleType

import fastr
from fastr.core.basemanager import BaseManager
from fastr.core.baseplugin import BasePlugin, Plugin, PluginState
import fastr.exceptions as exceptions


plugin_option_type = collections.namedtuple('plugin_option_type', ['filename', 'name', 'namespace', 'id'])


class BasePluginManager(BaseManager):
    """
    Baseclass for PluginManagers, need to override the self._plugin_class
    """

    def __init__(self, path=None, recursive=False):
        """
        Create a BasePluginManager and scan the give path for matching plugins

        :param str path: path to scan
        :param bool recursive: flag to indicate a recursive search
        :return: newly created plugin manager
        :raises FastrTypeError: if self._plugin_class is set to a class not
                                 subclassing BasePlugin
        """
        self._loaded_plugins = {}
        self._plugin_options = {}

        super(BasePluginManager, self).__init__(path, recursive)

        if not issubclass(self.plugin_class, BasePlugin):
            raise exceptions.FastrTypeError('Plugin type to manage ({}) not a valid plugin! (needs to be subclass of BasePlugin)'.format(self.plugin_class.__name__))

    def test_plugin(self, plugin):
        # Since we cannot know what Plugins might throw, catch all
        # pylint: disable=broad-except
        try:
            plugin.set_status(PluginState.preload, 'Set to PreLoad to perform testing')  # Let the Plugin think it is loaded, or it will refuse to instantiate
            plugin.test()
            plugin.set_status(PluginState.loaded, 'Testing successful, loaded properly')  # Let the Plugin think it is loaded, or it will refuse to instantiate
        # Register the configuration for the plugin
        except Exception as exception:
            fastr.log.warning('Could not load plugin file {}\n{}'.format(plugin.filename, exception))
            exc_type, _, _ = sys.exc_info()
            exc_info = traceback.format_exc()
            fastr.log.debug('Encountered exception ({}) during instantiation of the plugin:\n{}'.format(exc_type.__name__, exc_info))
            exception_stacktrace = ('Encountered exception ({}) during'
                                    ' instantiation of the plugin:\n{}').format(exc_type.__name__, exc_info)
            exception_message = '[{}] {}'.format(plugin.fullid, exception.message)
            plugin.set_status(PluginState.failed, exception_message, exception_stacktrace)

    def __getitem__(self, key):
        """
        Retrieve item from BaseManager

        :param key: the key of the item to retrieve
        :return: the value indicated by the key
        :raises FastrKeyError: if the key is not found in the BaseManager
        """
        try:
            plugin = super(BasePluginManager, self).__getitem__(key)
        except exceptions.FastrKeyError:
            self.load_plugin(key.lower())

            plugin = super(BasePluginManager, self).__getitem__(key)

        if plugin.status not in [PluginState.loaded, PluginState.failed]:
            self.test_plugin(plugin)

        return plugin

    @abstractproperty
    def plugin_class(self):
        """
        The class from which the plugins must be subclassed
        """
        raise exceptions.FastrNotImplementedError

    @property
    def _item_extension(self):
        """
        Plugins should be loaded from files with a .py extension
        """
        return '.py'

    @property
    def _instantiate(self):
        """
        Flag indicating that the plugin should be instantiated prior to saving
        """
        return True

    def _print_key(self, key):
        print_out = (self[key].status.value, key)

        return print_out

    def _print_value(self, val):
        """
        Function for printing values (plugins) in this manager

        :param BasePlugin val: value to print
        :return: print representation
        :rtype: str
        """
        if val._instantiate:
            val = type(val)

        print_out = '<{}: {}>'.format(val.__bases__[0].__name__, val.__name__)
        return print_out

    def _load_item(self, filepath, namespace):
        """
        Load a plugin

        :param str filepath: path of the plugin to load
        """
        name = os.path.basename(filepath)
        name = os.path.splitext(name)[0].lower()

        value = plugin_option_type(filename=filepath, name=name, namespace=namespace, id=None)

        self._plugin_options[name] = value

    def populate(self):
        """
        Populate the manager with the data. This is a method that will be
        called when the Managers data is first accessed. This way we avoid
        doing expensive directory scans when the data is never requested.
        """
        super(BasePluginManager, self).populate()

        for plugin_key in self._plugin_options.keys():
            if plugin_key in self._plugin_options:
                self.load_plugin(plugin_key)

        if 'VirtualFileSystem' not in self:
            self._store_item('VirtualFileSystem', fastr.vfs)

    def load_plugin(self, plugin_key):
        plugin_option = self._plugin_options[plugin_key]
        filepath = plugin_option.filename

        # Since we cannot know what Plugins might throw, catch all
        # pylint: disable=broad-except
        try:
            filebase, _ = os.path.splitext(os.path.basename(filepath))
            temp_module = imp.load_source(filebase, filepath)
            for name, obj in inspect.getmembers(temp_module):
                if inspect.isclass(obj):
                    if filebase.lower() != obj.__name__.lower():
                        fastr.log.debug('Plugin name and module do not match ({} vs {})'.format(obj.__name__, filebase))
                        continue

                    if not issubclass(obj, self.plugin_class):
                        fastr.log.debug('{} is not a subclass of {}'.format(obj, self.plugin_class))
                        continue

                    obj.filename = filepath
                    if not inspect.isabstract(obj):
                        if obj.status == PluginState.uninitialized:
                            obj.register_configuration()
                        elif obj.status not in (PluginState.loaded, PluginState.failed):
                            fastr.log.warning('Invalid Plugin status: {}!'.format(obj.status))

                        # Save the source in the obj
                        obj.set_code(inspect.getsource(obj))
                        obj.module = temp_module

                        if obj.instantiate:
                            fastr.log.debug('Store instantiated plugin')
                            self.test_plugin(obj)
                            self._store_item(name, obj())
                        else:
                            fastr.log.debug('Store uninstantiated plugin')
                            self._store_item(name, obj)

                    else:
                        fastr.log.debug('Skipping abstract Plugin: {} ({})'.format(name, filepath))

        except Exception as exception:
            fastr.log.warning('Could not load {} file {}\n{}'.format(self.plugin_class.__name__, filepath, exception))
            exc_type, _, _ = sys.exc_info()
            exc_info = traceback.format_exc()
            fastr.log.info('Encountered exception ({}) during loading of the plugin:\n{}'.format(exc_type.__name__, exc_info))
        finally:
            del self._plugin_options[plugin_key]


class PluginsView(collections.MutableMapping):
    """
    A collection that acts like view of the plugins of another plugin manager.
    This is a proxy object that only gives access the plugins of a certain
    plugin class. It behaves like a mapping and is used as the data object for
    a PluginSubManager.
    """
    def __init__(self, parent, plugin_class):
        """
        Constructor for the plugins view

        :param BasePluginManager parent: the parent plugin manager
        :param class plugin_class: the class of the plugins to expose
        """
        self.plugin_class = plugin_class
        self.parent = parent

    def filter_plugin(self, plugin):
        if self.plugin_class.instantiate and isinstance(plugin, self.plugin_class):
            return True
        elif not self.plugin_class.instantiate and issubclass(plugin, self.plugin_class):
            return True
        else:
            return False

    def __getitem__(self, item):
        result = self.parent[item]

        if not self.filter_plugin(plugin=result):
            raise KeyError(item)

        return result

    def __setitem__(self, key, value):
        if not self.filter_plugin(value):
            raise TypeError(value)

        if key in self.parent:
            if not self.filter_plugin(self.parent[key]):
                raise TypeError(key)

        self.parent[key] = value

    def __delitem__(self, key):
        if key in self.parent:
            if not self.filter_plugin(self.parent[key]):
                raise TypeError(key)

        del self.parent[key]

    def __len__(self):
        return sum(1 for v in self.parent.values() if self.filter_plugin(v))

    def __iter__(self):
        for key, value in self.parent.items():
            if not self.filter_plugin(value):
                continue

            yield key


class PluginSubManager(BasePluginManager):
    """
    A PluginManager that is a selection of a parent plugin manger. It uses the
    PluginsView to only exponse part of the parent PluginManager. This is used
    to create plugin managers for only certain types of plugins (e.g. IOPlugins)
    without loading them multiple times.
    """
    def __init__(self, parent, plugin_class):
        self.parent = parent
        self._plugin_class = plugin_class
        self._data_link = PluginsView(parent=parent, plugin_class=plugin_class)
        super(PluginSubManager, self).__init__()

    @property
    def data(self):
        return self._data_link

    @property
    def plugin_class(self):
        """
        PluginSubManagers only expose the plugins of a certain class
        """
        return self._plugin_class


class PluginManager(BasePluginManager):
    def __init__(self, path=None):
        if path is None:
            path = fastr.config.plugins_path

        super(PluginManager, self).__init__(path=path, recursive=True)

    @property
    def plugin_class(self):
        """
        The plugin manager contains any Plugin subclass
        """
        return Plugin

    def __setitem__(self, key, value):
        """
        Store an item in the BaseManager, will ignore the item if the key is
        already present in the BaseManager.

        :param name: the key of the item to save
        :param value: the value of the item to save
        :return: None
        """
        if not (isinstance(value, Plugin) or issubclass(value, Plugin)):
            raise TypeError(value)

        super(PluginManager, self).__setitem__(key, value)

    def _store_item(self, name, value):
        """
        Store an item in the BaseManager, will ignore the item if the key is
        already present in the BaseManager.

        :param name: the key of the item to save
        :param value: the value of the item to save
        :return: None
        """
        if name in self.keys():
            fastr.log.warning('Skipping {} from {} (the plugin is already in the {})'.format(name, value.filename, type(self).__name__))
        else:

            # Set the module to the fastr plugins
            if isinstance(value, BasePlugin):
                type(value).__module__ = 'fastr.plugins'
                setattr(fastr.plugins, value.id, type(value))
            else:
                value.__module__ = 'fastr.plugins'
                setattr(fastr.plugins, value.id, value)

            self[name] = value


class LazyModule(ModuleType):
    """
    A module that allows content to be loaded lazily from plugins. It generally
    is (almost) empty and gets (partially) populated when an attribute cannot be
    found. This allows lazy loading and plugins depending on other plugins.
    """
    def __init__(self, name, parent, plugin_manager):
        super(LazyModule, self).__init__(name)
        self._plugin_manager = plugin_manager
        self.__dict__.update(vars(parent))
        self._parent = parent
        sys.modules[parent.__name__] = self

    def __repr__(self):
        return super(LazyModule, self).__repr__().replace('module', 'lazy_module', 1)

    def __getattr__(self, item):
        """
        The getattr is called when getattribute does not return a value and is
        used as a fallback. In this case we try to find the value normally and
        will trigger the plugin manager if it cannot be found.

        :param str item: attribute to retrieve
        :return: the requested attribute
        """
        try:
            return super(LazyModule, self).__getattribute__(item)
        except AttributeError as exception:
            try:
                return self._plugin_manager[item]
            except KeyError:
                raise exception
