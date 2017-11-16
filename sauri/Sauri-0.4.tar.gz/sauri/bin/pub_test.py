from common.config import Config
from common import loginit
from messaging.broker import Broker
from messaging.factory import BrokerFactory

loginit.initTestLogging()

cfg = Config("cfg/home.yaml")
exchange = "Test"
topic = "test.topic"

for brokerConfig in cfg.brokers:
    broker = BrokerFactory.getBroker(brokerConfig)
    broker.publishOneShot(exchange, topic, "Test message")
    
    
    

