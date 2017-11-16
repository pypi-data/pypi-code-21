import ssl
import pika
import logging
from messaging.blocking.amqpbase import AMQPBase

logger = logging.getLogger(__name__)

class AMQPSubscriber(AMQPBase):
    """Blocking message amqp subscriber"""
    
    def __init__(self, host, port, caCertsFile, keyFile, certFile):
        """ Initialization of AMQP Subscriber
        
        Args:
            host (str):          FQDN or IP of broker
            port (int):          TCP port number to connect to the broker
            caCertsFile (str):   File container ca certificates
            keyFile (str):       File containing private key for AMQP client
            certFile (str):      File containing certificate for AMQP client
        """
        super(AMQPSubscriber, self).__init__(host, port, caCertsFile, keyFile, certFile)
        
    def subscribe(self, callback, topicNames, exchangeName, queueName='', options=None):
        """ Subscribe to events on a queue for multiple topics
        
        Args:
            callback (callable): Method to call when messages arrive on the queue
            topicNames (str[]):  Array of topicNames to filter on
            exchangeName (str):  Name of the exchange to join
            queueName (str):     Name of queue (optional)
            options (str{}):
                durable (bool):      Survive a reboot (optional)
                autoDelete(bool):    Delete when no queues subscribed (optional)
                noAck (bool):        Will auto acknowledge is set to True
                exclusive (bool):    Only allow the current connection to access the queue (optional)
                nowait (bool):       Don't wait for an answer (not yet supported)
                consumerTag(str):    Specify a consumer tag
            
        Returns:
            message (str): returns tuple of method object, properties, and the body
            
        """
        # set default options
        opts = {'durable':False, 'autoDelete':False, 'noAck':True, 'exclusive':True, 'noWait':False, 'consumerTag':None}
        # assign any user provided options
        if options is not None:
            for opt in options:
                opts[opt] = options[opt]
            
        self.createExchange(exchangeName)
        qn = self.createQueue(queueName=queueName,
                              durable=opts['durable'],
                              autoDelete=opts['autoDelete'],
                              exclusive=opts['exclusive'],
                              nowait=opts['noWait'])
        for topic in topicNames:
            self.bindToQueue(qn, exchangeName, topic)
            
        self.channel.basic_consume(consumer_callback=callback,
                                   queue=qn,
                                   no_ack=opts['noAck'],
                                   exclusive=opts['exclusive'],
                                   consumer_tag=opts['consumerTag'])
        
        self.channel.start_consuming()
        
    def unsubscribe(self):
        """ Usubscribe the channel"""
        self.channel.stop_consuming()
        

    
        