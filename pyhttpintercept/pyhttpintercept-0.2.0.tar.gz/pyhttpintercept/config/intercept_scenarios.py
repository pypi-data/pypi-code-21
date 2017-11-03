
import logging_helper
from configurationutil import Configuration, cfg_params, CfgItems, CfgItem
from .._metadata import __version__, __authorshort__, __module_name__
from ..resources.templates import intercept_template
from ..resources.schema import intercept_schema
from .constants import ScenarioConstant, INTERCEPT_SCENARIO_CONFIG

logging = logging_helper.setup_logging()

# Register Config details (These are expected to be overwritten by an importing app)
cfg_params.APP_NAME = __module_name__
cfg_params.APP_AUTHOR = __authorshort__
cfg_params.APP_VERSION = __version__

TEMPLATE = intercept_template.scenario
SCHEMA = intercept_schema.scenario


def _register_scenario_config():

    # Retrieve configuration instance
    cfg = Configuration()

    # Register configuration
    cfg.register(config=INTERCEPT_SCENARIO_CONFIG,
                 config_type=cfg_params.CONST.json,
                 template=TEMPLATE,
                 schema=SCHEMA)

    return cfg


class Modifier(CfgItem):

    def __init__(self,
                 **parameters):
        super(Modifier, self).__init__(**parameters)
        self.filter = self.filter.strip()  # Assume that we never want to

    def save_changes(self):

        updated_item = self.__dict__.copy()

        # remove any hidden parameters
        for k in [key for key in updated_item.keys()
                  if str(key).startswith(u'_')]:
            del updated_item[k]

        self._cfg[self._cfg_root][self._key_attr] = updated_item

    def passes_filter(self,
                      value,
                      wildcards=None,
                      case_sensitive=False):
        """
        :param value: value to check against filter (e.g. url)
        :param wildcards: A value or list of values that always match, e.g. '*'
        :param case_sensitive: Whether the checks should be case sensitive.
        :return: boolean
        """
        wildcards = (([wildcards]
                      if isinstance(wildcards, basestring)
                      else wildcards)
                     if wildcards else [])

        if not case_sensitive:
            return self.filter.lower() in value.lower() or self.filter.lower() in wildcards
        else:
            return self.filter in value or self.filter in wildcards


class Scenario(CfgItem):

    def __init__(self,
                 **parameters):
        super(Scenario, self).__init__(**parameters)

        self._load_modifiers()

    def _load_modifiers(self):

        for i, modifier in enumerate(self.modifiers):
            self.modifiers[i] = Modifier(cfg_fn=_register_scenario_config,
                                         cfg_root=u'{k}.{c}'.format(k=self._cfg_root,
                                                                    c=ScenarioConstant.modifiers),
                                         key=i,
                                         **modifier)

    def get_active_modifiers(self):
        return [modifier for modifier in self.modifiers if modifier.active]


class Scenarios(CfgItems):

    def __init__(self):
        super(Scenarios, self).__init__(cfg_fn=_register_scenario_config,
                                        cfg_root=INTERCEPT_SCENARIO_CONFIG,
                                        key=ScenarioConstant.name,
                                        has_active=False,
                                        item_class=Scenario)
