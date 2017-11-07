
from smartbotsol import StateMachine

import logging as logger
log = logger.getLogger(__name__)

class HandeledStateMachine(StateMachine):
    
    """
    State machine with telegram handlers functionality

    For each new message search handlers for current state
    if this does not exists returns FallbackState and next this return back to current state
    """

    def __init__(self, init_state, filters, fallback, handlers_not_required=True):
        self.fallback = fallback
        self.handlers_not_required = handlers_not_required
        super(HandeledStateMachine, self).__init__(init_state, filters)

    def collect_handlers(self, trigger, handlers):
        """returns set of handled updates"""
        # return set(name for name, candidate in handlers.items() if candidate.check_update(trigger.update))
        result = set()
        classname = self.state.__class__.__name__

        for name, candidate in handlers.items():
            log.info('Check update for "{}" {}'.format(name,candidate.check_update(trigger.update)))
            if candidate.check_update(trigger.update):
                result.add(name)
        log.debug('Found {} Handlers: {}'.format(classname, list(result)))
        return result


    def fire(self, trigger):
        log.debug('Resolve Handlers {}'.format(self.state.__class__.__name__))
        trigger.handler = set()
        classname = self.state.__class__.__name__


        #resolve entry point
        if classname == 'BootStrapState':
            log.debug('Check entry points for {}'.format(classname))
            for name, entry_point in self.state.handlers.items():
                if entry_point.check_update(trigger.update) or self.state.skip_start:
                    trigger.handler.add(name)
            log.debug('Found {} Handlers: {}'.format(classname, list(trigger.handler)))

        #search handler for update
        if classname not in ['BootStrapState', 'FallBackState'] and not trigger.handler:
            handlers = self.state.handlers
            trigger.handler = self.collect_handlers(trigger, handlers)

            #if handlers not exists go to FallbackState and search fallback
            if not trigger.handler:
                log.debug('Handlers not found')
                handlers = self.fallback.handlers

                self.fallback.parent = self.state # need to know where we came from when we get into FallbackState 
                self.to_state(self.fallback, trigger)
                log.debug('Check fallbacks: {}'.format(list(handlers.keys())))
                trigger.handler = self.collect_handlers(trigger, handlers)

        if trigger.handler or self.handlers_not_required:
            if self.state.__class__.__name__ in ['BootStrapState', 'FallbackState']:
                new_state = self.state._on_trigger(trigger)
                log.debug(new_state)
                self.to_state(new_state, trigger)
            else:
                super(HandeledStateMachine, self).fire(trigger)



