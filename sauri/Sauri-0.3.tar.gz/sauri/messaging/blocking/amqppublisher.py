import ssl
import logging
from messaging.blocking.amqpbase import AMQPBase

logger = logging.getLogger(__name__)

class AMQPPublisher(AMQPBase):
    """Blocking message amqp publisher"""
    
    def __init__(self, host, port, caCertsFile, keyFile, certFile):
        """ Initialization of AMQP publisher
        
        Args:
            host (str):          FQDN or IP of broker
            port (int):          TCP port number to connect to the broker
            caCertsFile (str):   File container ca certificates
            keyFile (str):       File containing private key for AMQP client
            certFile (str):      File containing certificate for AMQP client
        """
        super(AMQPPublisher, self).__init__(host, port, caCertsFile, keyFile, certFile)
            
    def publish(self, exchangeName, topicName, message):
        """ Publish message to exchange with routing key
        
        Args:
            exchangeName (str): Exchange to publish to
            topicName (str): Routing key name, such as anonymous.info
            message (str): Message to send to broker
            
        """
        self.createExchange(exchangeName)
        self.channel.basic_publish(exchange = exchangeName,
                                   routing_key = topicName,
                                   body = message)
        
    def publishOneShot(self, exchangeName, topicName, message):
        """ Connect, publish message, disconnect
        
        Args:
            same as publish

        """
        self.publish(exchangeName, topicName, message)
        self.disconnect()

    
            