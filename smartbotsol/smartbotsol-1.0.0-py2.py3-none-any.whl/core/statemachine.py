

import logging as logger
log = logger.getLogger(__name__)

class StateMachine(object):

    """
    Base implementation for StateMachine object
    """

    def __init__(self, init_state, filters):
        self.init_state = init_state
        self.filters = filters

    def fire(self, trigger):
        self.state = trigger.user.state
        if self.state is None:
            self.state = self.init_state
        for f in self.filters:
            filtered_state = f._on_process(self.state, trigger)
            if filtered_state:
                self.to_state(filtered_state, trigger)
                return

        new_state = self.state._on_trigger(trigger)
        self.to_state(new_state, trigger)
        trigger.user.state = self.state

    def to_state(self, new_state, trigger):
        if not new_state:
            return self.state

        if new_state == self.state:
            reenter_state = self.state._on_enter(trigger)
            self.to_state(reenter_state, trigger)
            return

        exit_state = self.state._on_exit(trigger)
        if exit_state:
            self.to_state(exit_state, trigger)
            return

        self.state = new_state

        enter_state = self.state._on_enter(trigger)
        if enter_state:
            self.to_state(enter_state, trigger)
            return
