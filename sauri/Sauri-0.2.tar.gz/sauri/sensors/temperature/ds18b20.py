import os.path
import time
import logging
from sensors.temperature.temperatureSensor import TemperatureSensor
from sensors.temperature.types import Type

logger = logging.getLogger(__name__)

class Ds18b20(TemperatureSensor):
    """Gets data from DS18B20 temperature sensor """
    def __init__(self, name, defaultUnit, path):
        """Initialize the sensor object """
        super(Ds18b20, self).__init__(name, Type.DS18B20, defaultUnit, path)
    
    def getRawData(self):
        """ Get the raw temperature reading from the sensor
        
        Sample:
            93 01 4b 46 7f ff 0d 10 32 : crc=32 YES
            93 01 4b 46 7f ff 0d 10 32 t=25187
        
        Returns:
            str[] : raw temperature reading
        """
        with open(self.sensorPath, 'r') as f:
            lines = f.readlines()
        f.close()
        return lines
    
    def getTempC(self, retries = 3):
        """ Get the temperature reading in Celsius
        
        Args:
            retries (int): (Optional) number of times to retry reading the sensor
        
        Returns:
            float : Temperature in Celsius if CRC is valid, otherwise returns None
        """
        temp = None
        lines = self.getRawData()
        try:
            while (self._isValid(lines[0]) == False) and (retries > 0):
                time.sleep(0.5)
                lines = self.getRawData()
                logger.debug("Raw data: {}".format(lines))
                retries = retries - 1
                if (self._isValid(lines[0])):
                    break
                elif (retries == 0):
                    #Early exit - we failed
                    logger.error("Invalid CRC from temperature sensor {} at {}".format(self.sensorName, self.sensorPath))
                    return temp
        
            #Parse it, it should be good
            temp = self._rawToC(lines[1])
            logger.debug("Got temp in {}C from {} at {}".format(temp, self.sensorName, self.sensorPath))
        except ValueError, ve:
            # Handle the case where the CRC is correct, but we get garbage on temp line
            logger.error("No temperature from sensor {} at {}".format(self.sensorName, self.sensorPath))
            temp = None
        except IndexError, ae:
            # Handle the case where the CRC is correct, but we get garbage on temp line
            logger.error("Empty temperature from sensor {} at {}".format(self.sensorName, self.sensorPath))
            temp = None
            
        return temp
    
    def getTempF(self, retries = 3):
        """ Get the temperature reading in Fahrenheit
        
        Args:
            retries (int): (Optional) number of times to retry reading the sensor
        
        Returns:
            float : Temperature in Fahrenheit if CRC is valid, otherwise returns None
        """
        tempC = self.getTempC(retries)
        if (tempC == None):
            return tempC
        else:
            tempF = tempC * 9 / 5 + 32
            logger.debug("Got temp in {}F from {} at {}".format(tempF, self.sensorName, self.sensorPath))
            return tempF
    
    def _rawToC(self, tempLine):
        """ Converts the raw temperature line to Celsius
        
        Args:
            tempLine (str): Full line from the raw reading
            
        Returns:
            float : Temperature in Celsius"""
        (junk, separator, rawTemp) = tempLine.partition(' t=')
        return float(rawTemp) / 1000.0
    
    def _isValid(self, crcLine):
        """ Checks if the CRC line is valid
        
        Args:
            crcLine (str): The first line from the sensor output
            
        Returns:
            bool : True is the CRC is valid, False if it is invalid
        """
        if 'YES' not in crcLine:
            return False
        else:
            return True
            
        
        
        