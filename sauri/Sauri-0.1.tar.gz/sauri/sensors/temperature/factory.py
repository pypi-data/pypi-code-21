from sensors.temperature.types import Type
from sensors.temperature.ds18b20 import Ds18b20
import logging

logger = logging.getLogger(__name__)

class TemperatureSensorFactory(object):
    """ Factory to create TemperatureSensor objects """
    def getTemperatureSensor(sensorConfig):
        """ Initialization of factory
        
        Args:
            sensorConfig (dict): subsection of configuration pertinent to this sensor
            
        Returns:
            TemperatureSensor : TemperatureSensor object
        """
        if (sensorConfig['type'] == Type.DS18B20):
            sensor = Ds18b20(sensorConfig['name'], sensorConfig['units'], sensorConfig['path'])
            return sensor
        else:
            logger.error("TemperatureSensor type {} not found".format(sensorConfig['type']))
            raise ValueError("TemperatureSensor type {} not found".format(sensorConfig['type']))
    getTemperatureSensor = staticmethod(getTemperatureSensor)
        