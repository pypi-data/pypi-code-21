import unittest
import logging
from common import loginit
from mock import Mock, patch, mock_open
from sensors.factory import SensorFactory
from sensors.temperature.ds18b20 import Ds18b20
from sensors.temperature.temperatureSensor import TemperatureSensor
from sensors.sensor import Sensor

class SensorFactoryTest(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        loginit.initTestLogging()
        SensorFactoryTest.logger = logging.getLogger(__name__)
        
    @patch('os.path.isfile')    
    def test_sensorGood(self, osMock):
        osMock.return_value = True
        cfg = {'category': 'temperature', 'path': '/sys/bus/w1/devices/28-000006156fd4', 'units': 'F', 'type': 'ds18b20', 'name': 'hotwaterBoilerFeed'}
        sensor = SensorFactory.getSensor(cfg)
        self.assertIsInstance(sensor, Ds18b20)
        self.assertIsInstance(sensor, TemperatureSensor)
        self.assertIsInstance(sensor, Sensor)
        
    @patch('os.path.isfile')    
    def test_sensorBad(self, osMock):
        osMock.return_value = True
        cfg = {'category': 'bad_cat', 'path': '/sys/bus/w1/devices/28-000006156fd4', 'units': 'F', 'type': 'ds18b20', 'name': 'hotwaterBoilerFeed'}
        with self.assertRaises(ValueError):
            sensor = SensorFactory.getSensor(cfg)
            
# Necessary to be able to run the unit test
if (__name__ == '__main__'):
    unittest.main()