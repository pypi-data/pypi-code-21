
import os
import logging_helper
from configurationutil import Configuration, cfg_params
from fdutil.path_tools import ensure_path_exists
from .._metadata import __version__, __authorshort__, __module_name__
from ..resources.templates import request_template
from ..resources.schema import request_schema
from .constants import INTERCEPT_CONFIG, InterceptKeysConstant

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

TEMPLATE = request_template.intercept
SCHEMA = request_schema.intercept


def _register_intercept_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=INTERCEPT_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=SCHEMA)

    return cfg


class InterceptConfig(object):

    def __init__(self):

        self._cfg = _register_intercept_config()

        self.modifier_paths = self._cfg[InterceptKeysConstant.modifier_paths]
        self.intercept_uris = self._cfg[InterceptKeysConstant.intercept_uris]

        ensure_path_exists(self.plugins_path)

    @property
    def plugins_path(self):
        return os.path.join(self._cfg.plugin_path, u'intercept_plugins')

    @property
    def selected_scenario(self):
        return self._cfg[InterceptKeysConstant.selected_scenario]

    @selected_scenario.setter
    def selected_scenario(self,
                          value):
        self._cfg[InterceptKeysConstant.selected_scenario] = value
