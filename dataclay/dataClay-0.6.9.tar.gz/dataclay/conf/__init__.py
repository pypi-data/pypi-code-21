"""Settings for dataClay application.

All settings for dataClay are defined here. Values will be read from the module
specified by the DATACLAY_SETTINGS_MODULE environment variable, and then from
dataclay.conf.global_settings.

Note that this code has been heavily inspired by the Django's conf module.
"""
import logging
import uuid

import os
from dataclay.conf.auto_loaders import AccountIdLoader, AccountCredentialLoader, AbstractLoader
from dataclay.core.exceptions import ImproperlyConfigured
from dataclay.core.properties import PropertyDict

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)

# Fields for the main properties file
FIELD_ACCOUNT = "Account"
FIELD_PASSWORD = "Password"
FIELD_STUBSFOLDER = "StubsClasspath"
FIELD_DATASETS = "DataSets"
FIELD_DATASETFORSTORE = "DataSetForStore"
FIELD_CLIENTCONFIG = "DataClayClientConfig"
FIELD_LOCAL_BACKEND = "LocalBackend"

# Fields for the client.properties file
FIELD_CLIENT_HOST = "HOST"
FIELD_CLIENT_TCPPORT = "TCPPORT"

UNSET_FIELD = object()


class _SettingsHub(object):
    """Application-wide configuration holder.

    This class holds values for all the configuration. It has some defaults,
    but a load from the properties file will overwrite the class values for
    specific instance values.

    Note that any lookup previous to a load_properties will raise an
    ImproperlyConfigured exception.
    """
    loaded = False

    def __init__(self):
        # Ensure a instance copy of the global class-default dictionary
        self._values = {
            'logicmodule_host': "127.0.0.1",
            'logicmodule_port': "2127",
            'logicmodule_rmiport': "2127",
            'network_timeout': 7200,

            'local_backend_name': None,

            'admin_user': os.getenv("DATACLAY_ADMIN_USER", "admin"),
            'admin_password': os.getenv("DATACLAY_ADMIN_PASSWORD", "admin"),
            'admin_id': AccountIdLoader(self, 'admin_user'),
            'admin_credential': AccountCredentialLoader(self, 'admin_id', 'admin_password'),

            'current_user': UNSET_FIELD,
            'current_password': UNSET_FIELD,
            'current_id': AccountIdLoader(self, 'current_user'),
            'current_credential': AccountCredentialLoader(self, 'current_id', 'current_password'),
            'current_session_id': UNSET_FIELD,

            'stubs_folder': UNSET_FIELD,

            'datasets': UNSET_FIELD,
            'dataset_for_store': UNSET_FIELD,
            'dataset_id': UNSET_FIELD,  # This is the DataSetID for the dataset_for_store

            'paraver_trace_output': "/tmp/output",
            'paraver_tracing_enabled': False,
        }

    def load_properties(self, file_name):
        """Load all the properties.

        Take a properties file and load all the settings used typically by the
        client application.
        """
        dirname = os.path.dirname(file_name)

        d = PropertyDict(file_name)
        logger.debug("Reading properties file %s", file_name)
        assert hasattr(d, FIELD_ACCOUNT)
        self._values["current_user"] = getattr(d, FIELD_ACCOUNT)

        assert hasattr(d, FIELD_PASSWORD)
        self._values["current_password"] = getattr(d, FIELD_PASSWORD)

        assert hasattr(d, FIELD_STUBSFOLDER)
        # Ensure real path, just in case, regarding the properties' file
        self._values["stubs_folder"] = os.path.realpath(os.path.join(
            dirname, getattr(d, FIELD_STUBSFOLDER)))

        assert hasattr(d, FIELD_DATASETS)
        self._values["datasets"] = getattr(d, FIELD_DATASETS).split(':')

        assert hasattr(d, FIELD_DATASETFORSTORE)
        self._values["dataset_for_store"] = getattr(d, FIELD_DATASETFORSTORE)

        assert hasattr(d, FIELD_CLIENTCONFIG)
        # Get relative to the path of the properties file, and clean up
        client_config_path = os.path.realpath(os.path.join(
            dirname, getattr(d, FIELD_CLIENTCONFIG)))

        self.load_connection(client_config_path)

        # Last thing to do is establish the "LOCAL" backend
        if hasattr(d, FIELD_LOCAL_BACKEND):
            self._values["local_backend_name"] = getattr(d, FIELD_LOCAL_BACKEND)

    def load_connection(self, file_name):
        """Load the connection settings values.

        This method may be used standalone or called from the more complete
        load_properties.
        """
        client_d = PropertyDict(file_name)

        assert hasattr(client_d, FIELD_CLIENT_HOST)
        self._values["logicmodule_host"] = getattr(client_d, FIELD_CLIENT_HOST)

        assert hasattr(client_d, FIELD_CLIENT_TCPPORT)
        self._values["logicmodule_port"] = int(getattr(client_d, FIELD_CLIENT_TCPPORT))

        # This method suffices for the load flag
        self.loaded = True

    def __getattr__(self, item):
        if not self.loaded:
            raise ImproperlyConfigured("The settings should be loaded before lookups")

        try:
            ret = self._values[item]
        except KeyError:
            raise ImproperlyConfigured("Key '%s' not recognized as a valid setting" % item)

        if ret is UNSET_FIELD:
            raise ImproperlyConfigured("The setting for '%s' has not been set" % item)

        if isinstance(ret, AbstractLoader):
            # if it is ready to be loaded, then load->store->return
            loaded = ret.load_value()
            self._values[item] = loaded
            return loaded
        else:
            return ret

    def __setattr__(self, key, value):
        if key == "loaded":
            assert value is True, "Unloading a settings is not permitted"
            object.__setattr__(self, key, value)
        elif key == "_values":
            # We expect that this is only done by the initialization
            object.__setattr__(self, key, value)
        else:
            self._values[key] = value


settings = _SettingsHub()
