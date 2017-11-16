from common.config import Config
from common import loginit
from messaging.broker import Broker
from messaging.factory import BrokerFactory

loginit.initTestLogging()

cfg = Config("cfg/home.yaml")
exchange = "Test"
topic = "test.topic"
topics = [topic]
broker = None

def messagePrinter(channel, method, props, body):
    print("Message received: {}:{}".format(method.routing_key,body))
    broker.unsubscribe()

for brokerConfig in cfg.brokers:
    broker = BrokerFactory.getBroker(brokerConfig)
    broker.subscribe(messagePrinter, topics, exchange)



