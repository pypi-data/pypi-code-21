""" Import abc dependency for abstraction """
from abc import ABC, abstractmethod

class PubSubService(ABC):
    """ A Publish Subscriber Service Abstract Class """

    @abstractmethod
    def publish(self, channel_name, event, payload):
        """ This allows to send an event and payload to the
            channel to the Publish Subscriber Service
        """
        pass
