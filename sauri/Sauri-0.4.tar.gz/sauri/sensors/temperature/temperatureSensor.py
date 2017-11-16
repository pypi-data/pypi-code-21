import os.path
import logging
from sensors.sensor import Sensor
from sensors.categories import Category
from sensors.temperature.types import Type

logger = logging.getLogger(__name__)

class TemperatureSensor(Sensor):
    """Generic temperature sensor interface"""
    def __init__(self, name, sensorType, defaultUnit, path):
        super(TemperatureSensor, self).__init__(name, Category.TEMPERATURE, sensorType, defaultUnit, path)
        
    def getRawData(self):
        raise NotImplementedError("Abstract base class: does not implement getRawData")
    
    def getTempC(self, retries):
        raise NotImplementedError("Abstract base class: does not implement getTempC")
    
    def getTempF(self, retries):
        raise NotImplementedError("Abstract base class: does not implement getTempF")
    
    def getData(self):
        if self.defaultUnit == Type.TEMPF:
            return self.getTempF()
        elif self.defaultUnit == Type.TEMPC:
            return self.getTempC()
        else:
            raise ValueError("Default Unit of {} no supported by TemperatureSensor".format(self.defaultUnit))