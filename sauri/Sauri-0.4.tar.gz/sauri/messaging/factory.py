from messaging.types import Type
from messaging.blocking.broker import BlockingBroker
import logging

logger = logging.getLogger(__name__)

class BrokerFactory(object):
    """ Factory to create broker objects """
    def getBroker(brokerConfig):
        """ Initialization of factory
        
        Args:
            brokerConfig (dict): subsection of configuration pertinent to this broker
            
        Returns:
            Broker : Broker object
        """
        if (brokerConfig['type'] == Type.BLOCKING):
            broker = BlockingBroker(brokerConfig)
            return broker
        else:
            logger.error("Broker type {} not found".format(brokerConfig['type']))
            raise ValueError("Broker type {} not found".format(brokerConfig['type']))
    getBroker = staticmethod(getBroker)