from messaging.types import Type
from messaging.blocking.protocols import Protocol
from messaging.blocking.amqppublisher import AMQPPublisher
from messaging.blocking.amqpsubscriber import AMQPSubscriber
import logging

logger = logging.getLogger(__name__)

class BlockingMessagerFactory(object):
    """ Factory to create BlockingMessager objects """
    def getBlockingPublisher(brokerConfig):
        """ Initialization of factory
        
        Args:
            brokerConfig (dict): subsection of configuration pertinent to this messager
            
        Returns:
            BlockingPublisher : BlockingPublisher object
        """
        if (brokerConfig['protocol'] == Protocol.AMQP):
            broker = AMQPPublisher(brokerConfig['address'],
                                   brokerConfig['port'],
                                   brokerConfig['ca_certs'],
                                   brokerConfig['key_file'],
                                   brokerConfig['cert_file'])
            return broker
        else:
            logger.error("BlockingPublisher protocol {} not found".format(brokerConfig['protocol']))
            raise ValueError("BlockingPublisherr protocol {} not found".format(brokerConfig['protocol']))
    getBlockingPublisher = staticmethod(getBlockingPublisher)
    
    def getBlockingSubscriber(brokerConfig):
        """ Initialization of factory
        
        Args:
            brokerConfig (dict): subsection of configuration pertinent to this messager
            
        Returns:
            BlockingSubscriber : BlockingSubscriber object
        """
        if (brokerConfig['protocol'] == Protocol.AMQP):
            broker = AMQPSubscriber(brokerConfig['address'],
                                   brokerConfig['port'],
                                   brokerConfig['ca_certs'],
                                   brokerConfig['key_file'],
                                   brokerConfig['cert_file'])
            return broker
        else:
            logger.error("BlockingSubscriber protocol {} not found".format(brokerConfig['protocol']))
            raise ValueError("BlockingSubscriber protocol {} not found".format(brokerConfig['protocol']))
    getBlockingSubscriber = staticmethod(getBlockingSubscriber)
    
    
    