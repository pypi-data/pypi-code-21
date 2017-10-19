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
This module defines the Fastr Config class for managing the configuration of
Fastr. The config object is stored directly in the fastr top-level module.
"""

import __builtin__
import collections
import inspect
import json
import logging
import logging.config
import multiprocessing
import os
import tempfile


logging.captureWarnings(True)


class EmptyDefault(object):
    """ Empty defaultdict. """
    def __init__(self, data=None):
        self._list_data = [NotImplemented]
        self._dict_data = collections.defaultdict(EmptyDefault)

        if isinstance(data, collections.Mapping):
            self._dict_data.update(data)
        elif isinstance(data, collections.Sequence):
            self._list_data = list(data)

    # Any object be added in place (just replaces current value)
    def __iadd__(self, right):
        self._list_data += right
        return self

    def __add__(self, right):
        return EmptyDefault(self._list_data + right)

    def __radd__(self, other):
        return EmptyDefault(other + self._list_data)

    def append(self, value):
        self._list_data.append(value)

    def prepend(self, value):
        self._list_data = [value] + self._list_data

    def extend(self, other):
        self._list_data.extend(other)

    # Make this act like a dict updated by another dict
    def update(self, other):
        self._dict_data.update(other)

    def __getitem__(self, item):
        return self._dict_data[item]

    def __setitem__(self, key, value):
        self._dict_data[key] = value

    def __delitem__(self, key):
        del self._dict_data[key]

    # Access to data
    def aslist(self):
        return list(self._list_data)

    def asdict(self):
        return dict(self._dict_data)


def _find_log_type():
    """
    Figure out the logtype to use for this fastr session

    :return: log type to us
    :rtype: str
    """
    # Use multiprocessing to check if we are actually in the MainProcess
    # Subprocesses should not log in a standard way
    current_process = multiprocessing.current_process()

    # Hack setting non-standard log methods/destinations before fastr is imported
    _stack = inspect.stack()
    for frame in _stack[1:]:
        if 'FASTR_LOG_TYPE' in frame[0].f_globals:
            fastr_log_type = frame[0].f_globals['FASTR_LOG_TYPE']

            # We only want to last definition of fastr_log_type
            break
    else:
        if current_process.name != 'MainProcess':
            #fastr_log_type = 'childprocess'
            fastr_log_type = 'default'
        else:
            fastr_log_type = 'default'

    return fastr_log_type


USER_DIR = os.path.expanduser(os.path.join('~', '.fastr'))
SYSTEM_DIR = os.path.abspath(os.path.normpath(os.path.dirname(__file__)))
RESOURCE_DIR = os.path.join(SYSTEM_DIR, 'resources')


class Config(object):
    """
    Class contain the fastr configuration
    """
    DEFAULT_FIELDS = {
        "logging_config": (
            dict,
            {},
            "Python logger config"
        ),
        "debug": (
            bool,
            False,
            "Flag to enable/disable debugging"
        ),
        "logtype": (
            str,
            _find_log_type(),
            "Type of logging to use"
        ),
        "loglevel": (
            int,
            20,
            "The log level to use (as int), INFO is 20, WARNING is 30, etc"
        ),
        "systemdir": (
            str,
            SYSTEM_DIR,
            "Fastr installation directory"
        ),
        "userdir": (
            str,
            USER_DIR,
            "Fastr user configuration directory",
            "~/.fastr"
        ),
        "logdir": (
            str,
            os.path.join(USER_DIR, 'logs'),
            "Directory where the fastr logs will be placed",
            "$userdir/logs"
        ),
        "resourcesdir": (
            str,
            RESOURCE_DIR,
            "Directory containing the fastr system resources",
            "$systemdir/resources"
        ),
        "examplesdir": (
            str,
            os.path.join(SYSTEM_DIR, 'examples'),
            "Directory containing the fastr examples",
            "$systemdir/examples"
        ),
        "schemadir": (
            str,
            os.path.join(SYSTEM_DIR, 'resources', 'schemas'),
            "Directory containing the fastr data schemas",
            "$systemdir/schemas"
        ),
        "executionscript": (
            str,
            os.path.join(SYSTEM_DIR, 'execution', 'executionscript.py'),
            "Execution script location",
            "$systemdir/execution/executionscript.py"
        ),
        "types_path": (
            list,
            [x for x in [os.path.join(USER_DIR, 'datatypes'), os.path.join(RESOURCE_DIR, 'datatypes')] if os.path.exists(x)],
            "Directories to scan for datatypes",
            ['$userdir/datatypes', '$resourcedir/datatypes']
        ),
        "tools_path": (
            list,
            [x for x in [os.path.join(USER_DIR, 'tools'), os.path.join(RESOURCE_DIR, 'tools')] if os.path.exists(x)],
            "Directories to scan for tools",
            ['$userdir/tools', '$resourcedir/tools']
        ),
        "networks_path": (
            list,
            [x for x in [os.path.join(USER_DIR, 'networks'), os.path.join(RESOURCE_DIR, 'networks')] if os.path.exists(x)],
            "Directories to scan for networks",
            ['$userdir/networks', '$resourcedir/networks']
        ),
        "plugins_path": (
            list,
            [x for x in [os.path.join(USER_DIR, 'plugins'), os.path.join(RESOURCE_DIR, 'plugins')] if os.path.exists(x)],
            "Directories to scan for plugins",
            ['$userdir/plugins', '$resourcedir/plugins']
        ),
        "mounts": (
            dict,
            {
                'tmp': tempfile.gettempdir(),
                'example_data': os.path.join(SYSTEM_DIR, 'examples', 'data'),
                'home': os.path.expanduser('~/'),
            },
            "A dictionary containing all mount points in the VFS system",
            {
                'tmp': '$TMPDIR',
                'example_data': '$systemdir/examples/data',
                'home': '~/'
            }
        ),
        "preferred_types": (
            list,
            [],
            "A list indicating the order of the preferred types to use. First item is most preferred."
        ),
        "protected_modules": (
            list,
            [],
            "A list of modules in the environmnet modules that are protected against unloading"
        ),
        "execution_plugin": (
            str,
            'ProcessPoolExecution',
            "The default execution plugin to use"
        ),
        "web_hostname": (
            str,
            'localhost',
            "The hostname to expose the web app for"
        ),
        "web_port": (
            str,
            '5000',
            "The port to expose the web app on"
        ),
        "web_secret_key": (
            str,
            'VERYSECRETKEY!',
            "The secret key to use for the flask web app"
        ),
        "warn_develop": (
            bool,
            True,
            "Warning users on import if this is not a production version of fastr"
        ),
        "source_job_limit": (
            int,
            0,
            "The number of source jobs allowed to run concurrently"
        ),
        "pim_host": (
            str,
            '',
            "Host of the PIM server to report to"
        ),
        "filesynchelper_url": (
            str,
            '',
            'Redis url e.g. redis://localhost:6379'
        )
    }

    # pylint: disable=too-many-instance-attributes
    # The config has many attributes, because its function is to hold
    # this data

    def __init__(self, *configfiles):
        #: Trace of the config files read by this object
        self.read_config_files = []
        self.log = None

        #: Raw config of current values
        self._fields = collections.OrderedDict(sorted(self.DEFAULT_FIELDS.items()))
        self._create_field_properties(self._fields)
        self._current_config = collections.defaultdict(EmptyDefault)
        self._current_config.update(vars(__builtin__))

        # Read default config files if found
        if os.environ.get('FASTRHOME'):
            if os.path.exists(os.path.join(os.environ['FASTRHOME'], 'config.py')):
                self.read_config(os.path.join(os.environ['FASTRHOME'], 'config.py'))
        elif os.path.exists(os.path.join(self.userdir, 'config.py')):
            self.read_config(os.path.join(self.userdir, 'config.py'))

        config_d = os.path.join(self.userdir, 'config.d')
        if os.path.isdir(config_d):
            for potential_config in sorted(os.listdir(config_d)):
                candidate = os.path.join(config_d, potential_config)
                if candidate.endswith('.py') and os.path.isfile(candidate):
                    self.read_config(candidate)

        # Read config files as parameters
        for filename in configfiles:
            if os.path.exists(filename):
                self.read_config(filename)
            else:
                self.log.error('Config file {} does not exist!'.format(filename))

        #: The logger used by fastr, set and updated by the Config object
        self._update_logging()

    def register_fields(self, fields_spec):
        """
        Register extra fields to the configuration manager.
        """
        if not isinstance(fields_spec, dict):
            raise TypeError("The fields_spec argument should be a dict")

        for name, field_spec in fields_spec.items():
            if name not in self._fields:
                self._fields[name] = field_spec
            else:
                if self._fields[name] != field_spec:
                    raise ValueError('Found a conflicting definition for the field {}'.format(name))

        self._create_field_properties(fields_spec)

    def get_field(self, item):
        if item in self._fields:
            # Get the field specification from the field definitions
            field_spec = self._fields[item]

            # Get the currently stored value of the config
            value = self._current_config.get(item, None)

            # Use the default in case the value is not found
            if value is None:
                value = field_spec[1]

            # Catch cases without a valid defautt
            if value is None:
                raise ValueError('No default given for {}'.format(item))

            # In case of dict/list, get data and merge with default
            if isinstance(value, EmptyDefault):
                if field_spec[0] is dict:
                    new_value = dict(field_spec[1])
                    new_value.update(value.asdict())
                    value = new_value
                elif field_spec[0] is list:
                    new_value = []
                    for x in value.aslist():
                        if x is not NotImplemented:
                            new_value.append(x)
                        else:
                            new_value.extend(field_spec[1])
                    value = new_value
                else:
                    raise TypeError('Config value and type do not match!')

            # Validate the type against the field specification
            if not isinstance(value, field_spec[0]):
                raise TypeError('Config value for {} is of wrong type, expected {}, found {}'.format(item,
                                                                                                     field_spec[0],
                                                                                                     type(value).__name__))

            return value
        else:
            raise KeyError('Field not found in config field specification!')

    def set_field(self, item, value):
        if item in self._fields:
            # Get the field specification from the field definitions
            field_spec = self._fields[item]

            if not isinstance(value, field_spec[0]):
                raise TypeError('Type mismatch, config field should be a {} found {}'.format(
                    field_spec[0],
                    type(value).__name__
                ))

            # Set the value
            self._current_config[item] = value
            self._update_logging()
        else:
            raise KeyError('Field not found in config field specification!')

    @classmethod
    def _create_field_properties(cls, fields):
        """
        Create properties for a dictionary of fields

        :param fields: The mapping of the fields to create
        """
        for field_name, field_value in fields.items():
            if not hasattr(cls, field_name):
                prop = cls._field_property(field_name, field_value[2])
                setattr(cls, field_name, prop)

    @staticmethod
    def _field_property(field_name, field_doc=None):
        """
        Create a property for a field
        :param field_name: the name of the field
        :param field_doc: the docstring for the field
        :return: property to use
        """
        def getter(obj):
            return obj.get_field(field_name)

        def setter(obj, value):
            obj.set_field(field_name, value)

        return property(getter, setter, field_doc)

    def __repr__(self):
        items = []

        for key, spec in self._fields.items():
            val = getattr(self, key)

            if isinstance(val, (dict, list, basestring)):
                val = json.dumps(val, indent=2)

            items.append("# [{s[0].__name__}] {s[2]}\n{k} = {v}\n".format(s=spec, k=key, v=val))

        return '\n'.join(items)

    def read_config(self, filename):
        """
        Read a configuration and update the configuration object accordingly

        :param filename: the configuration file to read
        """
        execfile(filename, {}, self._current_config)

        for key, value in self._current_config.items():
            if isinstance(value, (list, dict)):
                self._current_config[key] = EmptyDefault(value)

        self.read_config_files.append(filename)
        self._update_logging()

    def read_config_string(self, value):
        self.read_config_files.append('from string:\n{}'.format(value))
        exec(value, {}, self._current_config)

        for key, value in self._current_config.items():
            if isinstance(value, (list, dict)):
                self._current_config[key] = EmptyDefault(value)

        self._update_logging()

    def web_url(self):
        """ Construct a fqdn from the web['hostname'] and web['port'] settings.
        :return: FQDN
        :rtype: str
        """
        #if self.web['port'] == 80:
        #    return 'http://{}' .format(self.web['hostname'])
        #elif self.web['port'] == 443:
        #    return 'https://{}' .format(self.web['hostname'])
        #else:
        #    return 'http://{}:{}'.format(self.web['hostname'], self.web['port'])
        return 'http://localhost'

    def _update_logging(self):
        """
        Update the logging using the current config settings.
        """
        # Create log dir if needed (make sure it exists before other
        # operation requiring logging) but after logdir is known
        if not os.path.exists(self.logdir):
            os.makedirs(self.logdir)

        logging_definition = {
            'version': 1,
            'disable_existing_loggers': True,
            'formatters': {
                'verbose': {
                    'format': '[%(processName)s::%(threadName)s] %(levelname)s: %(module)s:%(lineno)d >> %(message)s'
                },
                'console_simple': {
                    'format': '[%(levelname)s] %(module) 9s:%(lineno)04d >> %(message)s'
                },
                'console_minimal': {
                    'format': '%(levelname)s >> %(message)s'
                },
            },
            'handlers': {
                'console': {
                    'level': self.loglevel,
                    'class': 'logging.StreamHandler',
                    'formatter': 'verbose' if self.debug else 'console_simple',
                    'stream': 'ext://sys.stdout',
                },
                'childprocess': {
                    'level': 'CRITICAL',
                    'class': 'logging.NullHandler',
                },
                'error_file': {
                    'level': 'ERROR',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'verbose',
                    'filename': os.path.join(self.logdir, 'error.log'),
                    'maxBytes': 10 * 1024 * 1024,
                    'backupCount': 20,
                },
                'info_file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'verbose',
                    'filename': os.path.join(self.logdir, 'info.log'),
                    'maxBytes': 10 * 1024 * 1024,
                    'backupCount': 20,
                },
                'server_file': {
                    'level': 'INFO',
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'verbose',
                    'filename': os.path.join(self.logdir, 'server.log'),
                    'maxBytes': 10 * 1024 * 1024,
                    'backupCount': 20,
                },
                'null_handler': {
                    'level': 'CRITICAL',
                    'class': 'logging.NullHandler',
                }
            },
            'loggers': {
                'fastr': {
                    'handlers': ['console', 'info_file', 'error_file'],
                    'propagate': True,
                    'level': 'DEBUG',
                },
                'py:warnings': {
                    'handlers': ['console', 'info_file', 'error_file'],
                    'propagate': True,
                }
            },
            'root': {
                'handlers': ['null_handler'],
                'level': 'DEBUG'
            }
        }

        fastr_log_type_options = {
            'default': ['console', 'info_file', 'error_file'],
            'server': ['server_file', 'console'],
            'daemon': ['server_file'],
            'console': ['console'],
            'childprocess': ['childprocess'],
            'worker': ['worker'],
            'none': ['null_handler']
        }

        logging_definition['loggers']['fastr']['handlers'] = fastr_log_type_options[self.logtype]

        if self.debug:
            logging_definition['handlers']['console']['level'] = 'DEBUG'
            logging_definition['handlers']['server_file']['level'] = 'DEBUG'
            logging_definition['handlers']['debug_file'] = {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'verbose',
                'filename': os.path.join(self.logdir, 'debug.log'),
                'maxBytes': 10 * 1024 * 1024,
                'backupCount': 20,
                }
            logging_definition['handlers']['childprocess'] = {
                'level': 'INFO',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
                'stream': 'ext://sys.stdout',
                }
            logging_definition['loggers']['fastr']['handlers'].append('debug_file')
        else:
            logging_definition['handlers']['console']['level'] = self.loglevel
            logging_definition['handlers']['server_file']['level'] = self.loglevel
            try:
                del logging_definition['handlers']['debug_file']
            except KeyError:
                pass
            try:
                logging_definition['loggers']['fastr']['handlers'].remove('debug_file')
            except ValueError:
                pass
            logging_definition['loggers']['fastr']['level'] = self.loglevel

        if self.logging_config: # we have a custom log config so we should override default settings with what is in config
            logging_definition = self._deep_update(logging_definition, self.logging_config)

        logging.config.dictConfig(logging_definition)
        if self.log is None:
            self.log = logging.getLogger('fastr')
            self.log.debug('Setting up the FASTR environment')
        else:
            self.log.debug('Updated fastr logging')
        self.log.debug('Log config: {}'.format(logging_definition))
        self.log.debug('Log directory: {}'.format(self.logdir))
        self.log.debug('Using log type: {} (debug: {})'.format(self.logtype, self.debug))

    def _deep_update(self, dict_left, dict_right):
        for key, value in dict_right.items():
            if isinstance(value, dict):
                result = self._deep_update(dict_left.get(key, {}), value)
                dict_left[key] = result
            else:
                dict_left[key] = dict_right[key]
        return dict_left
