import ssl
from pika import ConnectionParameters,BlockingConnection
from pika.exceptions import ConnectionClosed,ChannelClosed,ChannelError,AMQPConnectionError
import logging

logger = logging.getLogger(__name__)

class AMQPBase(object):
    """Blocking message amqp broker"""
    
    def __init__(self, host, port, caCertsFile, keyFile, certFile):
        """ Initialization of AMQP broker
        
        Args:
            host (str):          FQDN or IP of broker
            port (int):          TCP port number to connect to the broker
            caCertsFile (str):   File container ca certificates
            keyFile (str):       File containing private key for AMQP client
            certFile (str):      File containing certificate for AMQP client
        """
        self.host = host
        self.port = port
        self.caCertsFile = caCertsFile
        self.keyFile = keyFile
        self.certFile = certFile
        self.connection = None
        self.channel = None
        
    def connect(self):
        """ Connect to broker """
        logger.debug("Connecting to AMQP broker {}:{}".format(self.host, self.port))
        conn_params = ConnectionParameters(
                        host=self.host,
                        port=self.port,
                        ssl=True,
                        ssl_options=dict(
                            ssl_version=ssl.PROTOCOL_TLSv1_2,
                            ca_certs=self.caCertsFile,
                            keyfile=self.keyFile,
                            certfile=self.certFile,
                            cert_reqs=ssl.CERT_REQUIRED))

        if self.connection is not None:
            logger.debug("Connect called on {}:{}, but connection already defined.  Disconnecting and reconnecting".format(self.host, self.port))
            self.disconnect()
            
        self.connection = BlockingConnection(conn_params)
        self.channel = self.connection.channel()
        logger.debug("Connected to AMQP broker {}:{}".format(self.host, self.port))
        
    def reconnect(self):
        """ Check if the channel and connection are open, if not then reconnect"""
        logger.debug("Reconnecting to AMQP broker {}:{}".format(self.host, self.port))
        if self.connection is not None:
            self.disconnect()
        self.connect()
        
    def disconnect(self):
        """ Disconnect from broker """
        self.channel.close()
        self.channel = None
        self.connection.close()
        self.connection = None
        logger.debug("Disconnected from AMQP broker {}:{}".format(self.host, self.port))
        
    def createExchange(self, exchangeName, durable=False, autoDelete=False, nowait=False):
        """ Create a new exchange, if it doesn't exist
        
        Args:
            exchangeName (str): Name of the exchange
            durable (bool):     Survive a reboot
            autoDelete(bool):   Delete when no queues subscribed
            nowait (bool):      Don't wait for an answer (no supported yet)
            
        """
        try:
            self._createExchange(exchangeName, durable, autoDelete, nowait)
        except (ConnectionClosed, ChannelClosed, ChannelError, AMQPConnectionError, AttributeError) as cc:
            logger.info("Connection threw exception when trying to create exchange: {}, re-establishing connection...".format(cc))
            self.reconnect()
            # If it fails this time, let the exception through
            self._createExchange(exchangeName, durable, autoDelete, nowait)
            
    def _createExchange(self, exchangeName, durable, autoDelete, nowait):
        logger.info("Creating AMQP exchange {}".format(exchangeName))
        self.channel.exchange_declare(exchange=exchangeName,
                                      exchange_type='topic',
                                      passive = False,
                                      durable = durable,
                                      auto_delete = autoDelete)
        
    def createQueue(self, queueName='', durable=False, autoDelete=False, exclusive=False, nowait=False):
        """ Create a new queue, if it doesn't exist
        
        Args:
            queueName (str):     Name of queue (optional)
            durable (bool):      Survive a reboot (optional)
            autoDelete(bool):    Delete when no queues subscribed (optional)
            exclusive (bool):    Only allow the current connection to access the queue (optional)
            nowait (bool):       Don't wait for an answer (not supported yet)
            
        Returns:
            queueName (str): Name of the queue created
            
        """
        qn = None
        try:
            qn = self._createQueue(queueName, durable, autoDelete, exclusive, nowait)
        except (ConnectionClosed, ChannelClosed, ChannelError, AMQPConnectionError, AttributeError) as cc:
            logger.info("Connection threw exception when trying to create queue: {}, re-establishing connection...".format(cc))
            self.reconnect()
            # If it fails this time, let the exception through
            qn = self._createQueue(queueName, durable, autoDelete, exclusive, nowait)
            
        return qn
            
    def _createQueue(self, queueName, durable, autoDelete, exclusive, nowait):
        q = self.channel.queue_declare(queue=queueName,
                                       durable=durable,
                                       auto_delete=autoDelete,
                                       exclusive=exclusive)
        return q.method.queue
        
    def bindToQueue(self, queueName, exchangeName, topicName=None, nowait=False):
        """ Bind to a queue
        
        Args:
            queueName (str):     Name of queue (optional)
            exchangeName (str):  Name of exchange to use
            topicName (str):     Routing key name, such as anonymous.info
            nowait (bool):       Don't wait for an answer (not yet supported)
            
        """
        try:
            self._bindToQueue(queueName, exchangeName, topicName, nowait)
        except (ConnectionClosed, ChannelClosed, ChannelError, AMQPConnectionError, AttributeError) as cc:
            logger.info("Connection threw exception when trying to bind to queue: {}, re-establishing connection...".format(cc))
            self.reconnect()
            # If it fails this time, let the exception through
            self._bindToQueue(queueName, exchangeName, topicName, nowait)
            
    def _bindToQueue(self, queueName, exchangeName, topicName, nowait):
        self.channel.queue_bind(queue=queueName,
                                exchange=exchangeName,
                                routing_key=topicName)
        