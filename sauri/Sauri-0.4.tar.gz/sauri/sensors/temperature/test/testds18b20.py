import unittest
import logging
from common import loginit
from mock import Mock, patch, mock_open
from sensors.temperature.ds18b20 import Ds18b20

class Ds18b20Test(unittest.TestCase):

    goodData = "93 01 4b 46 7f ff 0d 10 32 : crc=32 YES\n93 01 4b 46 7f ff 0d 10 32 t=25187"
    badCrc = "93 01 4b 46 7f ff 0d 10 32 : crc=32 NO\n93 01 4b 46 7f ff 0d 10 32 t=25187"
    zeroTemp = "93 01 4b 46 7f ff 0d 10 32 : crc=32 YES\n93 01 4b 46 7f ff 0d 10 32 t=0"
    noTemp = "93 01 4b 46 7f ff 0d 10 32 : crc=32 YES\n93 01 4b 46 7f ff 0d 10 32 t="
    invalidTemp = "93 01 4b 46 7f ff 0d 10 32 : crc=32 YES\n93 01 4b 46 7f ff 0d 10 32 t=dfhg"
    empty = ""
    name = "testSensorName"
    du = 'F'

    @classmethod
    def setUpClass(cls):
        loginit.initTestLogging()
        Ds18b20Test.logger = logging.getLogger(__name__)
            
    @patch('os.path.isfile')
    def test_invalidPath(self, osMock):
         osMock.return_value = False
         with self.assertRaises(IOError):
            t = Ds18b20(Ds18b20Test.name, Ds18b20Test.du, "/tmp")
            
    @patch('os.path.isfile')
    def test_getName(self, osMock):
        osMock.return_value = True
        sensor = Ds18b20(Ds18b20Test.name, Ds18b20Test.du, "/file")
        self.assertEqual(sensor.getName(), Ds18b20Test.name)
        
    @patch('os.path.isfile')
    def test_getPath(self, osMock):
        osMock.return_value = True
        sensor = Ds18b20(Ds18b20Test.name, Ds18b20Test.du, "/file")
        self.assertEqual(sensor.getPath(), "/file")
        
    @patch('os.path.isfile')
    def test_getDefaultUnit(self, osMock):
        osMock.return_value = True
        sensor = Ds18b20(Ds18b20Test.name, Ds18b20Test.du, "/file")
        self.assertEqual(sensor.getDefaultUnit(), Ds18b20Test.du)
        
    @patch('os.path.isfile')
    def test_getTopicPrefix(self, osMock):
        osMock.return_value = True
        sensor = Ds18b20(Ds18b20Test.name, Ds18b20Test.du, "/file")
        self.assertEqual(sensor.getTopicPrefix(), "sensor.temperature.{}".format(Ds18b20Test.name))
        
    @patch('os.path.isfile')
    def _getSensor(self, osMock):
        osMock.return_value = True
        sensor = Ds18b20(Ds18b20Test.name, Ds18b20Test.du, "/file")
        return sensor
    
    def test_getCGood(self):
        sensor = self._getSensor()
        
        openMock = mock_open(read_data=Ds18b20Test.goodData)
        with patch('__builtin__.open', openMock) as mockFile:
            self.assertEqual(sensor.getTempC(), 25.187)
            
    def test_getFGood(self):
        sensor = self._getSensor()
        
        openMock = mock_open(read_data=Ds18b20Test.goodData)
        with patch('__builtin__.open', openMock) as mockFile:
            self.assertEqual(sensor.getTempF(), 77.3366)
            
    def test_getCBadCRC(self):
        sensor = self._getSensor()
        
        openMock = mock_open(read_data=Ds18b20Test.badCrc)
        with patch('__builtin__.open', openMock) as mockFile:
            self.assertEqual(sensor.getTempC(), None)
            
    def test_getCZero(self):
        sensor = self._getSensor()
        
        openMock = mock_open(read_data=Ds18b20Test.zeroTemp)
        with patch('__builtin__.open', openMock) as mockFile:
            self.assertEqual(sensor.getTempC(), 0.0)
            
    def test_getCNoTemp(self):
        sensor = self._getSensor()
        
        openMock = mock_open(read_data=Ds18b20Test.noTemp)
        with patch('__builtin__.open', openMock) as mockFile:
            self.assertEqual(sensor.getTempC(), None)
            
    def test_getCEmptyTemp(self):
        sensor = self._getSensor()
        
        openMock = mock_open(read_data=Ds18b20Test.empty)
        with patch('__builtin__.open', openMock) as mockFile:
            self.assertEqual(sensor.getTempC(), None)
                
    def test_getCInvalidTemp(self):
        sensor = self._getSensor()
        
        openMock = mock_open(read_data=Ds18b20Test.invalidTemp)
        with patch('__builtin__.open', openMock) as mockFile:
            self.assertEqual(sensor.getTempC(), None)
                
    def test_getFBadCRC(self):
        sensor = self._getSensor()
        
        openMock = mock_open(read_data=Ds18b20Test.badCrc)
        with patch('__builtin__.open', openMock) as mockFile:
            self.assertEqual(sensor.getTempF(), None)
        

# Necessary to be able to run the unit test
if (__name__ == '__main__'):
    unittest.main()