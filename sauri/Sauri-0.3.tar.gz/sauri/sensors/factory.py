from sensors.categories import Category
from sensors.temperature.factory import TemperatureSensorFactory
from common.config import Config

import logging

logger = logging.getLogger(__name__)

class SensorFactory(object):
    """ Factory to create Sensor objects """
    def getSensor(sensorConfig):
        """ Initialization of factory
        
        Args:
            sensorConfig (dict): subsection of configuration pertinent to this sensor
            
        Returns:
            Sensor : Sensor object
        """
        if (sensorConfig['category'] == Category.TEMPERATURE):
            sensor = TemperatureSensorFactory.getTemperatureSensor(sensorConfig)
            return sensor
        else:
            logger.error("Sensor category {} not found".format(sensorConfig['category']))
            raise ValueError("Sensor category {} not found".format(sensorConfig['category']))
    getSensor = staticmethod(getSensor)
    