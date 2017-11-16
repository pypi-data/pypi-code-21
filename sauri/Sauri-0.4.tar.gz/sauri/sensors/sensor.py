import os.path
import logging

logger = logging.getLogger(__name__)

class Sensor(object):
    """Generic sensor interface"""
    def __init__(self, name, sensorCategory, sensorType, defaultUnit, path):
        self.sensorName = name
        self.sensorCategory = sensorCategory
        self.sensorType = sensorType
        self.defaultUnit = defaultUnit
        self.topicPrefix = "sensor.{}.{}".format(self.sensorCategory, self.sensorName)
        if os.path.isfile(path):
            self.sensorPath = path
        else:
            logger.error("Sensor path {} does not exist".format(path))
            raise IOError("File {} does not exist".format(path))
        
    def getName(self):
        """ Return sensor name """
        return self.sensorName
    
    def getPath(self):
        """ Return sensor path """
        return self.sensorPath
    
    def getSensorCategory(self):
        """ Return sensor category """
        return self.sensorCategory
    
    def getSensorType(self):
        """ Return sensor type """
        return self.sensorType
    
    def getDefaultUnit(self):
        """ Return sensor default unit """
        return self.defaultUnit
    
    def getTopicPrefix(self):
        """ Return messaging topic prefix """
        return self.topicPrefix
    
    def getData(self):
        raise NotImplementedError("Abstract base class: does not implement getData")