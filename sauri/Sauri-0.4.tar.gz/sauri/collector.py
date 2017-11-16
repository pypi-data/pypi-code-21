from common.config import Config
from common import loginit
from time import sleep
from sensors.factory import SensorFactory
from sensors.sensor import Sensor
from sensors.temperature.temperatureSensor import TemperatureSensor
from messaging.broker import Broker
from messaging.factory import BrokerFactory
import argparse

loginit.initLogging()

exchange = "sauri"
sensors =[]
brokers = []

def parseArgs():
    parser = argparse.ArgumentParser(description='Simple sensor collector')
    parser.add_argument('-c', '--configFile', help='Full path to config file', required=True)
    parser.add_argument('-i', '--interval', type=int, default=30, help='Time between sensor collections in seconds')
    args = parser.parse_args()
    return args

def initialize(cfg):
    for brokerConfig in cfg.brokers:
        broker = BrokerFactory.getBroker(brokerConfig)
        brokers.append(broker)
        
    for sensorCfg in cfg.sensors:
        sensor = SensorFactory.getSensor(sensorCfg)
        sensors.append(sensor)

def runCollection():
    for sensor in sensors:
        reading = sensor.getData()
        topic = "{}.{}".format(sensor.topicPrefix, sensor.defaultUnit)
        for broker in brokers:
            broker.publish(exchange, topic, reading)
            
if (__name__ == '__main__'):
    args = parseArgs()
    cfg = Config(args.configFile)
    initialize(cfg)
    while True:
        runCollection()
        time.sleep(30)
        
