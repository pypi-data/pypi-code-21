# encoding: utf-8

import os
import sys
import copy
import importlib
import logging_helper
from collections import MutableMapping
from fdutil.list_tools import filter_list
from fdutil.path_tools import ensure_path_exists
from . import modifiers
from ._handler import InterceptHandlers
from ..config.intercept import InterceptConfig
from ..config.constants import ModifierConstant, ModifierPathConstant
from ..config.intercept_scenarios import Modifier

logging = logging_helper.setup_logging()


class InterceptModifiers(MutableMapping):

    def __init__(self):

        cfg = InterceptConfig()

        self.handlers = InterceptHandlers()

        # Ensure plugin path exists
        ensure_path_exists(os.path.join(cfg.plugins_path, u'modifiers'))

        self._modifier_paths = [
            {
                ModifierPathConstant.search_path: os.path.dirname(os.path.abspath(modifiers.__file__)),
                ModifierPathConstant.module_root: u'pyhttpintercept.intercept.modifiers'
            },  # Default modifier path
            {
                ModifierPathConstant.search_path: os.path.join(cfg.plugins_path, u'modifiers'),
                ModifierPathConstant.module_root: u'intercept_plugins.modifiers'
            },  # Plugin path
        ]

        # Add additional configured modifier paths
        for pth in cfg.modifier_paths:
            mod = importlib.import_module(pth)

            pth_cfg = {
                ModifierPathConstant.search_path: os.path.dirname(mod.__file__),
                ModifierPathConstant.module_root: pth
            }

            self._modifier_paths.append(pth_cfg)

        self.registered_modifiers = {}
        self.loaded_modifiers = []

        # Discover modifiers
        self.discover_all_modifiers()

    def load_all_modifiers(self):

        for modifier in self.registered_modifiers:
            self.load_modifier(modifier)

    def discover_all_modifiers(self):

        for pth in self._modifier_paths:

            search_path = pth.get(ModifierPathConstant.search_path)
            import_sys_path = pth.get(ModifierPathConstant.search_path).split(os.sep)
            module_root = pth.get(ModifierPathConstant.module_root)

            # Work out the path that should be added to sys.path
            for d in module_root.split(u'.')[::-1]:
                if import_sys_path[-1] == d:
                    import_sys_path.pop()

            import_sys_path = os.sep.join(import_sys_path)

            # Add modifiers path to sys path so we can import from the configured directory
            # Note: modules at top of modifier paths list cannot be overridden by modifier paths
            # further down the list.  Therefore you CANNOT override built-in modifiers!
            if import_sys_path not in sys.path:
                sys.path.append(import_sys_path)

            # Load modifiers from all configured modifier paths
            self.__discover_modifiers(search_path,
                                      modifier_root=module_root)

        # Check whether we found any modifiers
        if len(self.registered_modifiers) == 0:
            logging.warning(u'No modifiers found')

    def __discover_modifiers(self,
                             dir_path,
                             modifier_root=u'',
                             handler_key=u''):

        # Check modifier path is a directory
        if os.path.isdir(dir_path):
            # Get contents of folder
            module_dir_list = os.listdir(dir_path)

            # Filter the list to drop init & python compiled files
            module_dir_list = filter_list(module_dir_list,
                                          [u'__init__', u'.pyc'],
                                          exclude=True)

            # Filter the list to get only directories
            filtered_module_dir_list = filter_list(copy.deepcopy(module_dir_list),
                                                   [u'.py'],
                                                   exclude=True)

            # Filter the list to get loose modifiers
            filtered_module_file_list = filter_list(copy.deepcopy(module_dir_list),
                                                    [u'.py'])

            # Register modifiers in this dir
            for modifier in filtered_module_file_list:
                self.register_modifier(modifier_root=modifier_root,
                                       modifier_path=os.path.join(dir_path, modifier),
                                       handler=handler_key)

            # Register modifiers in sub-dirs
            for pth in filtered_module_dir_list:
                new_dir = pth.split(os.sep).pop()
                new_handler_key = new_dir if not handler_key else u'{key}.{dir}'.format(key=handler_key,
                                                                                        dir=new_dir)

                self.__discover_modifiers(os.path.join(dir_path, pth),
                                          modifier_root=modifier_root,
                                          handler_key=new_handler_key)

        else:
            logging.error(u'Modifier path {pth} is not a directory!'.format(pth=dir_path))

    def register_modifier(self,
                          modifier_root,
                          modifier_path,
                          handler):

        modifier_name = modifier_path.split(os.sep).pop().replace(u'.py', u'')
        module_key = (u'{handler}.{module}'.format(handler=handler,
                                                   module=modifier_name))

        # Check whether this modifier has already been registered.
        if module_key not in self.registered_modifiers:
            # Not registered yet so register the modifier.
            self.registered_modifiers[module_key] = {
                ModifierConstant.handler: handler,
                ModifierConstant.modifier_name: modifier_name,
                ModifierConstant.modifier_path: modifier_path,
                ModifierConstant.module_path: (u'{root}.{module_key}'.format(root=modifier_root,
                                                                             module_key=module_key))
            }

        else:
            # Modifier already registered, check whether this is the same or a different
            # modifier as the one already registered.
            m = self.registered_modifiers[module_key]

            if modifier_path == m[ModifierConstant.modifier_path]:
                logging.debug(u'Modifier {n} is already registered!'.format(n=modifier_name))

            else:
                logging.warning(u'Not loading modifier "{m}" from "{pth}" as another modifier with '
                                u'this name has already been registered!'.format(m=module_key,
                                                                                 pth=modifier_path))

    def load_modifier(self,
                      modifier):

        if isinstance(modifier, Modifier):
            modifier = u'{h}.{m}'.format(h=modifier[ModifierConstant.handler],
                                         m=modifier[ModifierConstant.modifier])

        try:
            mod = self.registered_modifiers[modifier]

        except KeyError:
            logging.warning(u'Cannot load modifier {m}. Modifier not registered!'.format(m=modifier))

        else:
            # Get handler for this modifier
            handler_name = mod[ModifierConstant.handler]
            handler = self.handlers.cfg.get_item(handler_name)

            # Ensure handler for this modifier is loaded
            self.handlers.load_handler(handler=handler)

            logging.debug(u'Loading modifier "{mod}" for handler "{key}".  '
                          u'Modifier path: {pth}'.format(mod=mod[ModifierConstant.modifier_name],
                                                         key=mod[ModifierConstant.handler],
                                                         pth=mod[ModifierConstant.modifier_path]))

            # Check whether this modifier has already been loaded, then either load/reload it.
            if modifier not in self.loaded_modifiers:
                self.__import_modifier_module(modifier_key=modifier,
                                              module_path=mod[ModifierConstant.module_path])

            else:
                logging.debug(u'Modifier "{n}" is already loaded, '
                              u'Reloading!'.format(n=mod[ModifierConstant.modifier_name]))

                reload(mod[ModifierConstant.module])
                self.__validate_modifier(modifier_key=modifier,
                                         modifier_module=mod[ModifierConstant.module],
                                         modifier_module_path=mod[ModifierConstant.module_path])

    def __import_modifier_module(self,
                                 modifier_key,
                                 module_path):

        try:
            modifier_module = importlib.import_module(module_path)

        except ImportError as err:
            logging.warning(u'Could not load modifier "{m}". {err}'.format(m=module_path,
                                                                           err=err))

        else:
            # Modifier module imported to lets instantiate the modifier!
            self.__validate_modifier(modifier_key=modifier_key,
                                     modifier_module=modifier_module,
                                     modifier_module_path=module_path)

    def __validate_modifier(self,
                            modifier_key,
                            modifier_module,
                            modifier_module_path):

        try:
            # Ensure modify function exists for modifier
            _ = modifier_module.modify

            self.registered_modifiers[modifier_key][ModifierConstant.module] = modifier_module

            if modifier_key not in self.loaded_modifiers:
                self.loaded_modifiers.append(modifier_key)

            logging.debug(u'Modifier loaded: {mod} - {m}'.format(mod=modifier_module_path,
                                                                 m=self.registered_modifiers[modifier_key]))

        except (AttributeError, NameError):
            logging.error(u'Modifier {modifier} not loaded as it does not contain a function '
                          u'called "modify"'.format(modifier=modifier_module_path))

    def __getitem__(self, item):
        return self.registered_modifiers[item]

    def __setitem__(self, item, value):
        self.registered_modifiers[item] = value

    def __delitem__(self, item):
        del self.registered_modifiers[item]

    def __iter__(self):
        return iter(self.registered_modifiers)

    def __len__(self):
        return len(self.registered_modifiers)
