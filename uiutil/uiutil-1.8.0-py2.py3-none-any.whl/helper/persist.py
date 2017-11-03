
import logging_helper; logging = logging_helper.setup_logging()

from .._metadata import __version__, __authorshort__, __module_name__
from ..resources import templates, schema
from stateutil.persist import Persist
from configurationutil import Configuration, cfg_params

from conversionutil.dx import dx
from conversionutil.ex import ex

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

# Set the config initialisation parameters
PERSISTENCE_CFG = u'ui_persist'
TEMPLATE = templates.ui_persist


class PersistentField(Persist):

    def __init__(self,
                 key,
                 *args,
                 **kwargs):

        self.cfg = Configuration()

        # Register configuration
        self.cfg.register(config=PERSISTENCE_CFG,
                          config_type=cfg_params.CONST.json,
                          template=TEMPLATE,
                          schema=schema.ui_persist)

        key = u'{c}.{k}'.format(c=PERSISTENCE_CFG,
                                k=key)

        super(PersistentField, self).__init__(persistent_store=self.cfg,
                                              key=key,
                                              *args,
                                              **kwargs)


class ObscuredPersistentField(PersistentField):
    """
    Used instead of PersistentField if you want
    the value stored with some noddy encoding
    """
    @staticmethod
    def encode(value):
        return ex(value)

    @staticmethod
    def decode(value):
        return dx(value)
