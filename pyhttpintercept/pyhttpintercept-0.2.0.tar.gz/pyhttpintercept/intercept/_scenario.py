# encoding: utf-8

import logging_helper
from ..exceptions import CircularReference
from ..config.intercept import InterceptConfig
from ._modifier import InterceptModifiers
from ..config.intercept_scenarios import Scenarios
from ..config.constants import ModifierConstant, ScenarioConstant

logging = logging_helper.setup_logging()


class InterceptScenario(object):

    def __init__(self):
        self._cfg = InterceptConfig()
        self._scenarios = Scenarios()
        self.modifiers = InterceptModifiers()
        self.handlers = self.modifiers.handlers  # Make handlers accessible

        self.scenario_handlers = []
        self.scenario_modifiers = []

        logging.debug(u'Active Scenario: {s}'.format(s=self.selected_scenario))

    @property
    def selected_scenario(self):
        return self._cfg.selected_scenario

    @selected_scenario.setter
    def selected_scenario(self,
                          value):
        self._cfg.selected_scenario = value

    def reload_active_scenario(self):

        self.scenario_handlers = []
        self.scenario_modifiers = []

        self.load_active_scenario()

    def load_active_scenario(self):
        logging.info(u'Loading active intercept scenario "{s}"'.format(s=self.selected_scenario))

        self.__get_scenario_modifiers(scenario_name=self.selected_scenario)

        # Load the modifiers for this scenario
        for modifier in self.scenario_modifiers:
            logging.debug(modifier)
            self.modifiers.load_modifier(modifier=modifier)

    def __get_scenario_modifiers(self,
                                 scenario_name,
                                 scenario_chain=None):

        if scenario_chain is None:
            scenario_chain = []

        if scenario_name in scenario_chain:
            raise CircularReference(u'"Ignoring circular reference ({scenario_name}) '
                                    u'in "{root_scenario}"\n{scenario_chain}'
                                    .format(scenario_name=scenario_name,
                                            root_scenario=scenario_chain[0],
                                            scenario_chain=(u'    scenario:,\n'.join(scenario_chain))))

        # Add this modifier to the chain.
        scenario_chain.append(scenario_name)

        scenario = self._scenarios.get_item(scenario_name)

        for modifier in scenario.get_active_modifiers():
            if modifier[ModifierConstant.handler].lower() == ScenarioConstant.scenario:
                nested_scenario_name = modifier[ModifierConstant.modifier]

                try:
                    self.__get_scenario_modifiers(scenario_name=nested_scenario_name,
                                                  scenario_chain=scenario_chain)

                except CircularReference as e:
                    logging.exception(e)

            else:
                self.scenario_modifiers.append(modifier)

                # add the handler for the modifier to the list of handlers for this scenario
                self.scenario_handlers.append(self.handlers.cfg.get_item(modifier[ModifierConstant.handler]))

        scenario_chain.pop()

        logging.debug(self.scenario_modifiers)
