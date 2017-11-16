import unittest
import logging
from common import loginit
from mock import Mock, patch, mock_open
from messaging.blocking.broker import BlockingBroker
from messaging.blocking.amqpsubscriber import AMQPSubscriber
from messaging.blocking.amqppublisher import AMQPPublisher
from pika.exceptions import ConnectionClosed,ChannelClosed,ChannelError,AMQPConnectionError

class BlockingBrokerTest(unittest.TestCase):
    
    config = {'name':'minix', 'protocol':'amqp', 'type':'blocking', 'address':'127.0.0.1', 'port':9999, 'ssl_pass':'pass',
              'ca_certs':'/home/ca.pem', 'key_file':'/home/key.pem', 'cert_file':'/home/cert.pem'}
    
    @classmethod
    def setUpClass(cls):
        loginit.initTestLogging()
        BlockingBrokerTest.logger = logging.getLogger(__name__)
        
    @patch('os.path.isfile')
    def test_goodInit(self, osMock):
        cfg = BlockingBrokerTest.config
        osMock.return_value = True
        
        broker = BlockingBroker(cfg)
        self.assertEqual(broker.brokerName, cfg['name'])
        self.assertEqual(broker.protocol, cfg['protocol'])
        self.assertEqual(broker.brokerType, cfg['type'])
        self.assertEqual(broker.host, cfg['address'])
        self.assertEqual(broker.port, cfg['port'])
        self.assertEqual(broker.caCertsFile, cfg['ca_certs'])
        self.assertEqual(broker.keyFile, cfg['key_file'])
        self.assertEqual(broker.certFile, cfg['cert_file'])
        self.assertEqual(broker.brokerConfig, cfg)
            
    @patch('os.path.isfile')
    def test_badCertsPath(self, osMock):
        cfg = BlockingBrokerTest.config
        osMock.return_value = False
        
        with self.assertRaises(IOError):
            b = BlockingBroker(cfg)
        
    @patch('messaging.blocking.amqpbase.BlockingConnection')
    def test_goodPublish(self, pikaMock):
        self.broker = self._getBroker()
        
        exchange = "testExchange"
        topic1 = "topic.one"
        msg = "Test message"
        self.broker.publish(exchange, topic1, msg)
        BlockingBrokerTest.logger.info("Pika calls: {}".format(pikaMock.mock_calls))

        # Make sure the channel and connection are NOT closed after publishing a message
        pikaMock.return_value.channel.return_value.basic_publish.assert_called_with(body=msg, exchange=exchange, routing_key=topic1)
        assert not pikaMock.return_value.channel.return_value.close.called
        assert not pikaMock.return_value.close.called
        
    @patch('messaging.blocking.amqpbase.BlockingConnection')
    def test_goodPublishOneShot(self, pikaMock):
        self.broker = self._getBroker()
        
        exchange = "testExchange"
        topic1 = "topic.one"
        msg = "Test message"
        self.broker.publishOneShot(exchange, topic1, msg)
        BlockingBrokerTest.logger.info("Pika calls: {}".format(pikaMock.mock_calls))

        # Make sure the channel and connection are cleaned up after calling one shot
        pikaMock.return_value.channel.return_value.basic_publish.assert_called_with(body=msg, exchange=exchange, routing_key=topic1)
        pikaMock.return_value.channel.return_value.close.assert_called
        pikaMock.return_value.close.assert_called
        
    @patch('messaging.blocking.amqpbase.BlockingConnection')
    def test_goodSubscribeOne(self, pikaMock):
        self.broker = self._getBroker()
        
        exchange = "testExchange"
        topic1 = "topic.one"
        topics = [topic1]
        self.broker.subscribe(self.testCallback, topics, exchange)

        pikaMock.return_value.channel.return_value.start_consuming.assert_called
        
        self.broker.unsubscribe()
        BlockingBrokerTest.logger.info("Pika unsubscribe calls: {}".format(pikaMock.mock_calls))
        pikaMock.return_value.channel.return_value.stop_consuming.assert_called
        
    @patch('messaging.blocking.amqpbase.BlockingConnection')
    def test_goodSubscribeThree(self, pikaMock):
        self.broker = self._getBroker()
        
        exchange = "testExchange"
        topic1 = "topic.one"
        topic2 = "topic.one.two"
        topic3 = "topic.one.two.three"
        topics = [topic1, topic2, topic3]
        self.broker.subscribe(self.testCallback, topics, exchange)
        
        # Test that we bound to all of the topics
        i = 0
        calls = pikaMock.return_value.channel.return_value.queue_bind.call_args_list
        for call in calls:
            args, kwargs = call
            BlockingBrokerTest.logger.info("Call {} with kwargs{}".format(i, kwargs))
            self.assertEquals(kwargs['exchange'], exchange)
            self.assertEquals(kwargs['routing_key'], topics[i])
            i = i + 1
                                           
        pikaMock.return_value.channel.return_value.start_consuming.assert_called
        
        self.broker.unsubscribe()
        pikaMock.return_value.channel.return_value.stop_consuming.assert_called
        
    @patch('messaging.blocking.amqpbase.BlockingConnection')
    def test_SubscribeBadSingleQueueBind(self, pikaMock):
        # ConnectionClosed
        pikaMock.return_value.channel.return_value.queue_bind.side_effect=[ConnectionClosed("Boom"), None]
        self.broker = self._getBroker()
        
        exchange = "testExchange"
        topic1 = "topic.one"
        topics = [topic1]
        self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.unsubscribe()
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_bind.side_effect=[ChannelClosed("Boom"), None]
        self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.unsubscribe()
        self.broker.disconnect()
         
        pikaMock.return_value.channel.return_value.queue_bind.side_effect=[ChannelError("Boom"), None]
        self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.unsubscribe()
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_bind.side_effect=[AMQPConnectionError("Boom"), None]
        self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.unsubscribe()
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_bind.side_effect=[AttributeError("Boom"), None]
        self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.unsubscribe()
        self.broker.disconnect()    
        
    @patch('messaging.blocking.amqpbase.BlockingConnection')
    def test_SubscribeBadDoubleQueueBind(self, pikaMock):
        pikaMock.return_value.channel.return_value.queue_bind.side_effect=[ConnectionClosed("Boom"), ConnectionClosed("Boom2")]
        self.broker = self._getBroker()
        
        exchange = "testExchange"
        topic1 = "topic.one"
        topics = [topic1]
        with self.assertRaises(ConnectionClosed):
            self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_bind.side_effect=[ChannelClosed("Boom"), ChannelClosed("Boom2")]
        with self.assertRaises(ChannelClosed):
            self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_bind.side_effect=[ChannelError("Boom"), ChannelError("Boom2")]
        with self.assertRaises(ChannelError):
            self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_bind.side_effect=[AMQPConnectionError("Boom"), AMQPConnectionError("Boom2")]
        with self.assertRaises(AMQPConnectionError):
            self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_bind.side_effect=[AttributeError("Boom"), AttributeError("Boom2")]
        with self.assertRaises(AttributeError):
            self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.disconnect()
        
    @patch('messaging.blocking.amqpbase.BlockingConnection')
    def test_SubscribeBadSingleQueueCreate(self, pikaMock):
        # ConnectionClosed
        pikaMock.return_value.channel.return_value.queue_declare.side_effect=[ConnectionClosed("Boom"), pikaMock.return_value.channel.return_value.queue_declare.return_value]
        self.broker = self._getBroker()
        
        exchange = "testExchange"
        topic1 = "topic.one"
        topics = [topic1]
        self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.unsubscribe()
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_declare.side_effect=[ChannelClosed("Boom"), pikaMock.return_value.channel.return_value.queue_declare.return_value]
        self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.unsubscribe()
        self.broker.disconnect()
         
        pikaMock.return_value.channel.return_value.queue_declare.side_effect=[ChannelError("Boom"), pikaMock.return_value.channel.return_value.queue_declare.return_value]
        self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.unsubscribe()
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_declare.side_effect=[AMQPConnectionError("Boom"), pikaMock.return_value.channel.return_value.queue_declare.return_value]
        self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.unsubscribe()
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_declare.side_effect=[AttributeError("Boom"), pikaMock.return_value.channel.return_value.queue_declare.return_value]
        self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.unsubscribe()
        self.broker.disconnect()    
        
    @patch('messaging.blocking.amqpbase.BlockingConnection')
    def test_SubscribeBadDoubleQueueCreate(self, pikaMock):
        pikaMock.return_value.channel.return_value.queue_declare.side_effect=[ConnectionClosed("Boom"), ConnectionClosed("Boom2")]
        self.broker = self._getBroker()
        
        exchange = "testExchange"
        topic1 = "topic.one"
        topics = [topic1]
        with self.assertRaises(ConnectionClosed):
            self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_declare.side_effect=[ChannelClosed("Boom"), ChannelClosed("Boom2")]
        with self.assertRaises(ChannelClosed):
            self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_declare.side_effect=[ChannelError("Boom"), ChannelError("Boom2")]
        with self.assertRaises(ChannelError):
            self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_declare.side_effect=[AMQPConnectionError("Boom"), AMQPConnectionError("Boom2")]
        with self.assertRaises(AMQPConnectionError):
            self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.disconnect()
        
        pikaMock.return_value.channel.return_value.queue_declare.side_effect=[AttributeError("Boom"), AttributeError("Boom2")]
        with self.assertRaises(AttributeError):
            self.broker.subscribe(self.testCallback, topics, exchange)
        self.broker.disconnect()
        
        
    @patch('os.path.isfile')
    def _getBroker(self, osMock):
        osMock.return_value = True
        return BlockingBroker(BlockingBrokerTest.config)
    
    def testCallback(self):
        return True
    
    def exceptOnce(self, exception, throwBool):
        if throwBool is True:
            return exception
        
        
# Necessary to be able to run the unit test
if (__name__ == '__main__'):
    unittest.main()
        
    