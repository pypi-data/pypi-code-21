
import logging_helper
from configurationutil import Configuration, cfg_params, CfgItems, CfgItem
from .._metadata import __version__, __authorshort__, __module_name__
from ..resources.templates import request_template
from ..resources.schema import request_schema
from .constants import HOSTING_CONFIG, HostingConstant

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

TEMPLATE = request_template.host
SCHEMA = request_schema.host


def _register_hosting_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=HOSTING_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=SCHEMA)

    return cfg


class Site(CfgItem):

    def __init__(self,
                 **parameters):
        super(Site, self).__init__(**parameters)


class Sites(CfgItems):

    def __init__(self):
        super(Sites, self).__init__(cfg_fn=_register_hosting_config,
                                    cfg_root=HOSTING_CONFIG,
                                    key=HostingConstant.path,
                                    has_active=HostingConstant.active,
                                    item_class=Site)
