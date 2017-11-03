import shutil
from tempfile import mkdtemp

import os
from appdirs import AppDirs
from jsonschema import SchemaError, ValidationError, Draft4Validator

import logging_helper
from classutils.singleton import SingletonType
from configurationutil.cfg_providers.json_provider import JSONConfig
from configurationutil.cfg_providers.yaml_provider import YAMLConfig
from fdutil.list_tools import filter_list
from fdutil.path_tools import pop_path, ensure_path_exists

logging = logging_helper.setup_logging()

# App details
APP_NAME = None  # Once Configuration is initialised changes to this parameter will be ignored!
APP_AUTHOR = None  # Once Configuration is initialised changes to this parameter will be ignored!
APP_VERSION = None  # Once Configuration is initialised changes to this parameter will be ignored!

CACHE_FOLDER = u'cache'
LOGS_FOLDER = u'logs'
PLUGIN_FOLDER = u'plugins'

VERSION_IGNORE_LIST = [
    CACHE_FOLDER,
    LOGS_FOLDER,
    PLUGIN_FOLDER
]


# Export constants
class _CONST:

    def __init__(self): pass

    # Master config properties
    @property
    def master_template(self): return u'master_config_template.json'

    @property
    def master_schema(self): return u'master_config_schema.json'

    @property
    def master_fn(self): return u'master_config.json'

    @property
    def master_registered(self): return u'registered_cfg'

    # Config Keys
    @property
    def cfg_dir(self): return u'config'

    @property
    def cfg_schema(self): return u'schema'

    @property
    def cfg_template(self): return u'template'

    @property
    def cfg_src_schema(self): return u'src_schema'

    @property
    def cfg_src_template(self): return u'src_template'

    @property
    def cfg_fn(self): return u'filename'

    @property
    def cfg_type(self): return u'type'

    # Available Config types
    @property
    def json(self): return u'json'

    @property
    def yaml(self): return u'yaml'

CONST = _CONST()  # Initialise Constants


# Config Types
CFG_TYPES = {
    CONST.json: {
        u'class': JSONConfig,
        u'ext': u'json'
    },
    CONST.yaml: {
        u'class': YAMLConfig,
        u'ext': u'yaml'
    }
}

# Schema Types
SCHEMA_TYPES = {
    u'string': str,
    u'number': float,
    u'object': dict,
    u'array': list,
    u'boolean': bool,
    u'null': None
}


class Configuration(object):

    __metaclass__ = SingletonType

    def __init__(self,
                 preload=False):

        """ Initialise Config class

            APP_NAME Must be set before initialisation.
            APP_AUTHOR is optional
            APP_VERSION is optional

            :param preload: Set True to preload all config objects
        """

        logging.info(u'Initialising configuration...')

        # Initialisation fails if APP_NAME has not been configured!
        if APP_NAME is None:
            raise ValueError(u'Cannot initialise configuration: APP_NAME not defined.')

        # Prepare app_dirs so we can setup paths
        self.__app_kwargs = {
            u'appname': APP_NAME
        }

        if APP_AUTHOR is not None:
            self.__app_kwargs[u'appauthor'] = APP_AUTHOR

        # Get reference to version agnostic paths for version checking
        self.__app_dirs_all_versions = AppDirs(**self.__app_kwargs)

        # Set version agnostic paths
        self.__basic_app_dirs = AppDirs(**self.__app_kwargs)

        if APP_VERSION is not None:
            self.__app_kwargs[u'version'] = APP_VERSION

        # Set paths to users OS default locations.
        self.__app_dirs = AppDirs(**self.__app_kwargs)

        logging.info(u'Config file path: {p}'.format(p=self.config_path))
        logging.debug(u'Config schema path: {p}'.format(p=self.schema_path))
        logging.debug(u'Config template path: {p}'.format(p=self.template_path))
        logging.debug(u'Cache path: {p}'.format(p=self.cache_path))
        logging.info(u'Data path: {p}'.format(p=self.data_path))
        logging.info(u'Log path: {p}'.format(p=self.log_path))

        # Set temp path
        self.__temp_path = mkdtemp(prefix=u'{app_name}_Temp_'.format(app_name=APP_NAME))
        logging.info(u'Temp path: {p}'.format(p=self.temp_path))

        # Set the master config path.  Any config required for this class to work will be stored here.
        self.__master_cfg_file = os.path.join(self.config_path, u'master_config.json')

        # Load the master config schema
        self.__master_cfg_schema_file = os.path.join(pop_path(__file__), CONST.master_schema)
        self.__master_cfg_schema_obj = self.__get_schema_obj(self.__master_cfg_schema_file)

        # Initialise master config
        self.__master_cfg = self.__init_cfg(config_file=self.__master_cfg_file,
                                            config_type=CONST.json,
                                            template=os.path.join(pop_path(__file__), CONST.master_template),
                                            schema=self.__master_cfg_schema_file)

        # Keep reference to registered configurations
        self.__registered_cfg = self.__master_cfg.cfg.get(u'registered_cfg')  # Keep a record of all registered config.
        self.__registered_cfg_objs = {}  # Keeping this record separate as they should not be dumped into config files.

        # If preload is set attempt to preload each registered config.
        if preload:
            for cfg in self.__registered_cfg:
                try:
                    self.__load_cfg(config=cfg)

                except (SchemaError, ValidationError) as err:
                    logging.warning(u'Failed pre-loading {cfg}: {err}'.format(cfg=cfg,
                                                                              err=err))

        logging.info(u'Configuration initialised.')

    def __init_cfg(self,
                   config_file,
                   config_type,
                   template=None,
                   schema=None):

        """ Initialise the config file

        If this is the first run the config will be created (either blank, from template or from previous config),
        otherwise, it will be loaded.

        :param config_file: Path to config file being created / loaded
        :param config_type: Config type from types available in CFG_TYPES.
        :param template:    Path to template file
        :param schema:      Path to schema file
        """

        cfg_type = CFG_TYPES.get(config_type)
        cfg_class = cfg_type.get(u'class')

        new = False if os.path.exists(config_file) else True

        cfg_obj = cfg_class(config_file=config_file,
                            create=True)

        if new:
            # initialise from a template (this is done whether template is set or not as there should be a default
            # template provided with the config class being initialised)
            self.__init_from_template(cfg_obj=cfg_obj,
                                      config_type=config_type,
                                      template=template,
                                      schema=schema)

        # If a schema is specified make sure the cfg_obj is valid before returning
        # If the schema is invlaid this raises SchemaError.
        # If cfg_obj is invalid this raises ValidationError.
        if schema is not None:
            self.__validate_config(schema, cfg_obj)

        return cfg_obj

    def __init_from_template(self,
                             cfg_obj,
                             config_type,
                             template=None,
                             schema=None):

        """ Initialise the configuration object from provided template

        :param cfg_obj:     Config object to initialise
        :param config_type: Config type from types available in CFG_TYPES.
        :param template:    Path to template file
        :param schema:      Path to schema file
        """

        cfg_type = CFG_TYPES.get(config_type)
        cfg_class = cfg_type.get(u'class')

        # Load template
        cfg_template_obj = cfg_class(config_file=template if template is not None else cfg_class.DEFAULT_TEMPLATE)

        # Validate & apply template
        try:
            if schema is not None:
                self.__validate_config(schema, cfg_template_obj)

            # This will only apply the config if the template has a valid schema
            cfg_obj.cfg = cfg_template_obj.cfg
            cfg_obj.save()

        except SchemaError as err:
            logging.error(u'Invalid schema for config template: {err}'.format(err=err))
            cfg_template_obj = None

        except ValidationError as err:
            logging.error(u'Template configuration is invalid: {err}'.format(err=err))
            cfg_template_obj = None

        return cfg_template_obj

    @staticmethod
    def __get_previous_versions(path):

        """ Check for and return the previous versions available

        :param path: The path in which to check for previous versions.

        :return:     List of version numbers (floats).
        """

        previous_versions = filter_list(os.listdir(path),
                                        filters=VERSION_IGNORE_LIST,
                                        exclude=True,
                                        case_sensitive=False)

        valid_previous_versions = []

        for item in previous_versions:
            try:
                valid_previous_versions.append(tuple(int(i) for i in item.split(u'.')))

            except ValueError:
                logging.warning(u'Ignoring "{item}". It is not a recognised version number'
                                .format(item=item))
                VERSION_IGNORE_LIST.append(item)

        valid_previous_versions.sort()

        previous_versions = [u'.'.join(map(unicode, item)) for item in valid_previous_versions]

        return previous_versions

    def __get_last_version(self):

        """ Work out the latest version of the app installed (not including the loaded version)

        Note: logs a warning if current version is older than the latest available

        :return: version number (float)
        """

        # Get the previous versions
        previous_versions = self.previous_versions

        #  filter out the current version
        if self.app_version in previous_versions:
            del previous_versions[previous_versions.index(self.app_version)]

        ver = previous_versions.pop() if len(previous_versions) > 0 else None

        if ver > self.app_version and ver is not None:
            logging.warning(u'You are running a version of config older than has been previously installed!')

        return ver

    def __load_cfg(self,
                   config):

        """ Load config file

        :param config: The name of the config to load.
        """

        if self.check_registration(config=config):
            cfg = self.__registered_cfg.get(config)

            cfg_type = CFG_TYPES.get(cfg.get(CONST.cfg_type))
            cfg_class = cfg_type.get(u'class')

            try:
                cfg_obj = cfg_class(config_file=os.path.join(self.config_path, cfg.get(CONST.cfg_fn)))

            except IOError:
                cfg_obj = self.__init_cfg(config_file=os.path.join(self.config_path, cfg.get(CONST.cfg_fn)),
                                          config_type=cfg.get(CONST.cfg_type),
                                          template=cfg.get(CONST.cfg_template),
                                          schema=cfg.get(CONST.cfg_schema))

            self.__validate_registered_config(config=config,
                                              obj=cfg_obj)

        else:
            raise KeyError(u'Cannot load config: {cfg}; Config not registered.'.format(cfg=config))

        self.__registered_cfg_objs[config] = cfg_obj

    def __reload_cfg(self,
                     config):

        """ Reload config file

        :param config: The name of the config to reload.
        """
        if self.check_registration(config):
            # Remove object if loaded
            if self.__check_loaded(config):
                del self.__registered_cfg_objs[config]

            # Load the config
            self.__load_cfg(config)

        else:
            raise KeyError(u'Cannot reload config: {cfg}; Config not registered.'.format(cfg=config))

    def register(self,
                 config,
                 config_type,
                 template=None,
                 schema=None):

        """ Register a config file.

        :param config:          The name of the config item being registered.  This will also be the filename.
        :param config_type:     The type of file this config item will be.
        :param template:        Template file to initialise config from.
        :param schema:          Schema file, conforming to the JSON schema format, to validate config with.
        """

        # Try upgrade first
        self.__upgrade_cfg(config,
                           template=template,
                           schema=schema)

        if not self.check_registration(config):
            cfg_type = CFG_TYPES.get(config_type)

            if cfg_type is None:
                raise LookupError(u'Config Type not found: {c}'.format(c=config_type))

            cfg_filename = u'{c}.{ext}'.format(c=config,
                                               ext=cfg_type.get(u'ext'))

            self.__init_cfg(config_file=os.path.join(self.config_path, cfg_filename),
                            config_type=config_type,
                            template=template,
                            schema=schema)

            self.__registered_cfg[config] = {
                CONST.cfg_fn: cfg_filename,
                CONST.cfg_type: config_type
            }

            # TODO: Validate schema & template before creating / registering any files!
            # Currently if a validation error is raised during registration a default file is created that has to be
            # manually remove before a valid file can be created!
            if template is not None:
                self.__register_template(config,
                                         template,
                                         cfg_type.get(u'ext'))

            if schema is not None:
                self.__register_schema(config, schema)

            self.__validate_master_config()  # if invalid this raises either SchemaError or ValidationError.
            self.__master_cfg.save()

            logging.info(u'Configuration registered: {cfg}'.format(cfg=config))

        else:
            logging.debug(u'Configuration already registered: {cfg}'.format(cfg=config))

    def unregister(self,
                   config):

        """ Unregister a config file.  This will also delete the config file.

        :param config:  The name of the config item being unregistered.
        """

        if self.check_registration(config):

            # Get paths & remove the config file
            paths = [
                {
                    u'fn': self.__registered_cfg[config].get(CONST.cfg_fn),
                    u'pth': self.config_path
                },
                {
                    u'fn': self.__registered_cfg[config].get(CONST.cfg_template),
                    u'pth': self.template_path
                },
                {
                    u'fn': self.__registered_cfg[config].get(CONST.cfg_schema),
                    u'pth': self.schema_path
                }
            ]

            for pth in paths:
                if pth.get(u'fn') is not None:
                    os.remove(os.path.join(pth[u'pth'], pth[u'fn']))

            # Remove registration
            del self.__registered_cfg[config]
            self.__master_cfg.save()

            # Remove object if loaded
            if self.__check_loaded(config):
                del self.__registered_cfg_objs[config]

            logging.info(u'Configuration unregistered: {cfg}'.format(cfg=config))

        else:
            logging.debug(u'Configuration does not exist: {cfg}'.format(cfg=config))

    def check_registration(self, config):

        """ Check whether config is already registered.

        :param config:  The name of the config item being checked.
        :return: boolean.  True if already registered.
        """

        return True if config in self.__registered_cfg.keys() else False

    def __upgrade_cfg(self,
                      config,
                      template=None,
                      schema=None):

        """ Upgrade a config file

        :param config:          The name of the config item being upgraded.  This will also be the filename.
        :param template:        Template file to initialise parameters from if not present in previous config.
        :param schema:          Schema file, conforming to the JSON schema format, to validate upgraded config with.
        """

        # TODO: This method is too big, try and refactor it.

        # Check if we have the config registered.  If yes assume already upgraded.
        if not self.check_registration(config):
            # Check for previous config version.
            previous_version = self.last_version

            if previous_version is not None:
                # load previous master config
                master_cfg_type = CFG_TYPES.get(CONST.json)
                master_cfg_class = master_cfg_type.get(u'class')
                old_master_path = os.path.join(self.__app_dirs_all_versions.user_config_dir,
                                               previous_version, CONST.cfg_dir, CONST.master_fn)

                old_master = master_cfg_class(config_file=old_master_path)

                # Try and get the config from our previous master
                previous_registration = old_master[CONST.master_registered].get(config)

                # if exists then perform upgrade.
                if previous_registration is not None:
                    # get required properties from previous
                    config_fn = previous_registration[CONST.cfg_fn]
                    config_type = previous_registration[CONST.cfg_type]

                    # Create the registration
                    self.__registered_cfg[config] = {
                        CONST.cfg_fn: config_fn,
                        CONST.cfg_type: config_type
                    }

                    # Get optional properties from previous
                    config_template_fn = previous_registration.get(CONST.cfg_template)
                    config_schema_fn = previous_registration.get(CONST.cfg_schema)

                    config_file = os.path.join(self.config_path, config_fn)
                    old_config_file = os.path.join(self.__app_dirs_all_versions.user_config_dir,
                                                   previous_version, CONST.cfg_dir, config_fn)

                    cfg_type = CFG_TYPES.get(config_type)

                    if cfg_type is None:
                        raise LookupError(u'Config Type not found: {c}'.format(c=config_type))

                    cfg_class = cfg_type.get(u'class')

                    # Check if previous version has a template
                    if config_template_fn is not None:
                        old_template = os.path.join(self.__app_dirs_all_versions.user_config_dir,
                                                    previous_version, CONST.cfg_dir, config_template_fn)

                        # If no template is specified for this version then carry forward template from previous
                        if template is None:
                            template = old_template

                    # Handle template

                    if template is not None:
                        self.__register_template(config,
                                                 template,
                                                 cfg_type.get(u'ext'))

                    # Load the previous config
                    old_cfg = cfg_class(config_file=old_config_file)

                    # Check if previous version has a schema
                    old_config_invalid = False
                    old_schema_invalid = False
                    if config_schema_fn is not None:
                        old_schema = os.path.join(self.__app_dirs_all_versions.user_config_dir,
                                                  previous_version, CONST.cfg_dir, config_schema_fn)

                        if os.path.exists(old_schema):
                            # Check if schema is specified for this version
                            if schema is None:
                                # No, then carry forward schema from previous
                                schema = old_schema

                            else:
                                # Yes, then validate the previous config against its own schema
                                try:
                                    self.__validate_config(old_schema, old_cfg)

                                except SchemaError as err:
                                    logging.error(u'Invalid schema for old config: {err}'.format(err=err))
                                    old_schema_invalid = True

                                except ValidationError as err:
                                    logging.error(u'Old configuration is invalid: {err}'.format(err=err))
                                    old_config_invalid = True

                    # Handle schema
                    schema_obj = None
                    if schema is not None:
                        self.__register_schema(config, schema)

                        # Load the schema
                        schema_obj = self.__get_schema_obj(schema)

                    # Validate & save master config
                    self.__validate_master_config()  # If invalid this raises either SchemaError or ValidationError.
                    self.__master_cfg.save()

                    # Create new config
                    cfg_obj = cfg_class(config_file=config_file,
                                        create=True)

                    # Load template
                    cfg_template_obj = self.__init_from_template(cfg_obj=cfg_obj,
                                                                 config_type=config_type,
                                                                 template=template,
                                                                 schema=schema)

                    exclude_properties = []

                    try:
                        if schema_obj is not None and not old_config_invalid and not old_schema_invalid:
                            # Validate old config against the new schema

                            v = Draft4Validator(schema_obj.cfg)

                            for error in v.iter_errors(old_cfg.cfg):
                                logging.debug(error.message)
                                if error.validator == u'required':
                                    for value in error.validator_value:
                                        if value not in old_cfg:
                                            logging.info(u'Required item missing, Adding: {v}'.format(v=value))
                                            if cfg_template_obj is not None:
                                                cfg_obj[value] = cfg_template_obj[value]

                                            else:
                                                properties = error.schema.get(u'properties')

                                                if properties is not None:
                                                    if value not in properties:
                                                        raise error

                                                    else:
                                                        prop_type = properties[value][u'type']
                                                        cfg_obj[value] = SCHEMA_TYPES[prop_type]()

                                                else:
                                                    raise error

                                elif error.validator == u'additionalProperties' and not error.validator_value:
                                    logging.info(u'Additional properties not allowed, Excluding from upgrade.')

                                    properties = error.schema.get(u'properties')

                                    if properties is not None:
                                        for prop in old_cfg:
                                            if prop not in properties:
                                                exclude_properties.append(prop)
                                                logging.debug(u'Excluding: {p}'.format(p=prop))

                                else:
                                    logging.error(u'Unhandled schema validation error')
                                    raise error

                    except ValidationError as err:
                        logging.warning(u'Old configuration is invalid with new schema: {err}'.format(err=err))

                    else:
                        # Upgrade the config
                        for cfg_key, cfg_item in iter(old_cfg.cfg.items()):
                            if cfg_key not in exclude_properties:
                                cfg_obj.cfg[cfg_key] = cfg_item

                    # Validate & Save config
                    try:
                        if schema is not None:
                            # Validate config against the schema
                            self.__validate_config(schema, cfg_obj)

                    except ValidationError as err:
                        logging.warning(u'Upgrade Failed, Configuration is invalid: {err}'.format(err=err))
                        self.unregister(config)

                    else:
                        # Save the configuration
                        cfg_obj.save()
                        logging.info(u'Configuration Upgraded: {cfg}'.format(cfg=config))

    def __check_loaded(self, config):

        """ Check whether config is already loaded.

        :param config:  The name of the config item being checked.
        :return: boolean.  True if already loaded.
        """

        if config not in self.__registered_cfg.keys():
            return False

        return True if config in self.__registered_cfg_objs.keys() else False

    def __register_template(self,
                            config,
                            template,
                            ext):

        """ Register a template to a config

        NOTE: This does not save the master config!

        :param config:      The config object to register the template to.
        :param template:    The path to the template being registered.
        :param ext:         The Template file extension.
        """

        if not os.path.exists(template):
            raise IOError(u'Template does not exists: {t}'.format(t=template))

        # Place a copy of the template in self.template_path
        ensure_path_exists(self.template_path)
        template_copy_fn = u'{cfg}.template.{ext}'.format(cfg=config,
                                                          ext=ext)
        template_copy = os.path.join(self.template_path, template_copy_fn)
        shutil.copyfile(template, template_copy)

        # Register the template
        self.__registered_cfg[config][CONST.cfg_template] = template_copy_fn

    def __register_schema(self,
                          config,
                          schema):

        """ Register a schema to a config

        NOTE: This does not save the master config!

        :param config:      The config object to register the template to.
        :param schema:      The path to the schema being registered.
        """

        if not os.path.exists(schema):
            raise IOError(u'Schema does not exists: {s}'.format(s=schema))

        # Place a copy of the schema in self.schema_path
        ensure_path_exists(self.schema_path)
        schema_copy_fn = u'{cfg}.schema.{ext}'.format(cfg=config,
                                                      ext=CONST.json)
        schema_copy = os.path.join(self.schema_path, schema_copy_fn)
        shutil.copyfile(schema, schema_copy)

        # Register the schema
        self.__registered_cfg[config][CONST.cfg_schema] = schema_copy_fn

    def __get_config_obj(self,
                         config):

        """ Get and return config object (loading it where necessary)

        :param config:  The config object requested
        :return:        An object exporting pre-defined config obj methods with the specified config loaded
        """

        if not self.__check_loaded(config):
            self.__load_cfg(config)

        return self.__registered_cfg_objs.get(config)

    @staticmethod
    def __get_schema_obj(schema_path):

        """ Loads and returns the schema object from the provided path.

        :param schema_path: Full path to schema file
        :return: Json schema object
        """

        # Load schema
        schema_type = CFG_TYPES.get(CONST.json)
        schema_class = schema_type.get(u'class')
        schema_obj = schema_class(config_file=schema_path)

        # Validate schema.  If invalid this will raise SchemaError
        Draft4Validator.check_schema(schema_obj.cfg)

        return schema_obj

    def __validate_config(self,
                          schema_path,
                          obj):

        """ Validate the provided config object against its schema if a schema is available.

        :param schema_path:  The path to the schema file to be used for validation
        :param obj:          The Config object to be validated
        """

        # Load schema
        schema_obj = self.__get_schema_obj(schema_path)

        # Ensure loaded config is still valid (i.e any external modification hasn't corrupted it)
        validator = Draft4Validator(schema_obj.cfg)
        validator.validate(obj.cfg)

    def __validate_master_config(self):

        """ Validate the master config object against its schema.

        """

        # Ensure master config is still valid (i.e any modification hasn't corrupted it)
        validator = Draft4Validator(self.__master_cfg_schema_obj.cfg)
        validator.validate(self.__master_cfg.cfg)

    def __validate_registered_config(self,
                                     config,
                                     obj):

        """ Validate the provided config object against its schema if a schema is available.

        :param config: The config that the config object relates to (so we can retrieve the schema
        :param obj:    The Config object to be validated
        """

        cfg = self.__registered_cfg.get(config)
        schema = cfg.get(CONST.cfg_schema)

        if schema is not None:
            # Load schema
            schema_path = os.path.join(self.schema_path, schema)
            self.__validate_config(schema_path, obj)

    def __validate_and_save_registered_config(self,
                                              config,
                                              obj):

        """ Validate the provided config object against its schema if a schema is available
            saving the config on successful validation.

        :param config: The config that the config object relates to (so we can retrieve the schema
        :param obj:    The Config object to be validated
        """

        # Validate the config
        try:
            self.__validate_registered_config(config, obj)

        except ValidationError:
            # Reload the config to keep the config valid
            self.__reload_cfg(config)

            # pass the exception on
            raise

        else:
            # If all is well we can save the object
            obj.save()

    def __validate_config_key(self, key):

        """ Get and return config item

        :param key: The config key to be validated
        :return:    obj - The config object for the validated config key,
                    config - The entry from the registered config dict,
                    items - List of items to traverse for the requested config value.
        """

        keys = key.split(u'.')

        if len(keys) > 1:

            config = keys[0]
            items = u'.'.join(keys[1:])

        else:
            # We requested the entire config file?!
            config = key
            items = None

        obj = self.__get_config_obj(config)  # This will raise a KeyError if the config is not registered.

        return obj, config, items

    def __getitem__(self, key):

        """ Get and return config item

        :param key: The config key used to retrieve the config item
        :return:    The requested config item
        """

        obj, config, items = self.__validate_config_key(key)

        if items is None:
            # Entire config was requested!
            return obj.cfg

        else:
            try:
                return obj[items]

            except KeyError:
                raise KeyError(u'Item key ({i}) not found'.format(i=key))

    def __setitem__(self, key, value):

        """ Set and return config item

        :param key:     The config key used to retrieve the config item
        :param value:   The new value for the config item
        """

        obj, config, items = self.__validate_config_key(key)

        # Update the config
        if items is None:
            # Entire config overwrite was requested!
            obj.cfg = value

        else:
            # Update & validate the item (where schema is present)
            # This includes adding any nodes that don't already exist
            obj[items] = value

        # Validate & save the config
        self.__validate_and_save_registered_config(config, obj)

    def __delitem__(self, key):

        """ Delete the specified config item

        :param key: The config key used to retrieve the config item being deleted
        """

        obj, config, items = self.__validate_config_key(key)

        if items is None:
            # Delete entire config?!  This is what the unregister function is for!
            # We raise an error rather than call unregister for the user to avoid accidental config removal!
            raise ValueError(u'Removal of the entire config via the del method is not supported; '
                             u'Please use the Configuration.unregister method instead!')

        else:
            # Delete & validate the item (where schema is present)
            del obj[items]

            # Validate & save the config
            self.__validate_and_save_registered_config(config, obj)

    def find(self,
             key,
             filters=None):

        """ Get a filtered list of config items

        NOTE: Find is not recursive and will only search the first level of the key provided.

        :param key:     The config item to run the search on.
        :param filters: List of filter tuples.
                        Tuple format: (Search Key, Search Value, Condition)
                        First should not have a condition
                        i.e [("A", 123), ("A", 789, u'AND')]
                        NOTE: if filters is None the entire key value will be returned.
        :return: dict containing the subset of matching items
        """

        # This will raise a KeyError if the config is not registered.
        obj, _, items = self.__validate_config_key(key)

        return obj.find(items, filters)

    def get_temp_path(self,
                      folder=None):

        folder_path = self.temp_path

        if folder:
            folder_path = os.sep.join((folder_path, folder))

        ensure_path_exists(folder_path)

        return folder_path

    # Properties
    @property
    def config_path(self):
        return os.path.join(self.__app_dirs.user_config_dir, CONST.cfg_dir)

    @property
    def schema_path(self):
        return os.path.join(self.__app_dirs.user_config_dir, CONST.cfg_schema)

    @property
    def template_path(self):
        return os.path.join(self.__app_dirs.user_config_dir, CONST.cfg_template)

    @property
    def data_path(self):
        return self.__app_dirs.user_data_dir

    @property
    def data_path_unversioned(self):
        return self.__basic_app_dirs.user_data_dir

    @property
    def cache_path(self):
        return self.__basic_app_dirs.user_cache_dir

    @property
    def log_path(self):
        return self.__basic_app_dirs.user_log_dir

    @property
    def temp_path(self):
        return self.__temp_path

    @property
    def plugin_path(self):
        return os.path.join(self.data_path_unversioned, u'plugins')

    @property
    def app_name(self):
        return self.__app_kwargs.get(u'appname')

    @property
    def app_version(self):
        return self.__app_kwargs.get(u'version')

    @property
    def app_author(self):
        return self.__app_kwargs.get(u'appauthor')

    @property
    def previous_versions(self):
        return self.__get_previous_versions(self.__app_dirs_all_versions.user_config_dir)

    @property
    def last_version(self):
        return self.__get_last_version()
