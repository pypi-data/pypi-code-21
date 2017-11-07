import logging as log


class BaseState(object):
    
    """
    Base implementation for State object
    """

    def __str__(self):
        return self.__class__.__name__

    def on_trigger(self, trigger):
        pass

    def _on_trigger(self, trigger):
        log.debug('== ' + str(self))
        return self.on_trigger(trigger)

    def on_enter(self, trigger):
        pass

    def _on_enter(self, trigger):
        log.debug('-> ' + str(self))
        return self.on_enter(trigger)

    def on_exit(self, trigger):
        pass

    def _on_exit(self, trigger):
        log.debug('<- ' + str(self))
        return self.on_exit(trigger)