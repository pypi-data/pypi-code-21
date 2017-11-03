
import logging_helper
from configurationutil import Configuration, cfg_params, CfgItems, CfgItem
from .._metadata import __version__, __authorshort__, __module_name__
from ..resources.templates import intercept_template
from ..resources.schema import intercept_schema
from .constants import HandlerConstant, INTERCEPT_HANDLER_CONFIG

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

TEMPLATE = intercept_template.handler
SCHEMA = intercept_schema.handler


def _register_handler_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=INTERCEPT_HANDLER_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=SCHEMA)

    return cfg


class Handler(CfgItem):

    def __init__(self,
                 **parameters):
        super(Handler, self).__init__(**parameters)


class Handlers(CfgItems):

    def __init__(self):
        super(Handlers, self).__init__(cfg_fn=_register_handler_config,
                                       cfg_root=INTERCEPT_HANDLER_CONFIG,
                                       key=HandlerConstant.name,
                                       has_active=False,
                                       item_class=Handler)
