from common.config import Config
from common import loginit
from time import sleep
from sensors.factory import SensorFactory
from sensors.sensor import Sensor
from sensors.temperature.temperatureSensor import TemperatureSensor
from messaging.broker import Broker
from messaging.factory import BrokerFactory

loginit.initLogging()

cfg = Config("cfg/home.yaml")
exchange = "sauri"
sensors =[]
brokers = []

def initialize():
    for brokerConfig in cfg.brokers:
        broker = BrokerFactory.getBroker(brokerConfig)
        brokers.append(broker)
        
    for sensorCfg in cfg.sensors:
        sensor = SensorFactory(sensorCfg)
        sensors.append(sensor)

def runCollection():
    for sensor in sensors:
        reading = sensor.getData()
        topic = "{}.{}".format(sensor.topicPrefix, sensor.defaultUnit)
        for broker in brokers:
            broker.publish(exchange, topic, reading)
            
if (__name__ == '__main__'):
    initialize()
    while True:
        runCollection()
        time.sleep(30)
        
