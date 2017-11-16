import unittest
import logging
from common import loginit
from mock import Mock, patch, mock_open
from sensors.temperature.ds18b20 import Ds18b20

class TempSensorTest(unittest.TestCase):
    
    goodData = "93 01 4b 46 7f ff 0d 10 32 : crc=32 YES\n93 01 4b 46 7f ff 0d 10 32 t=25187"
    badCrc = "93 01 4b 46 7f ff 0d 10 32 : crc=32 NO\n93 01 4b 46 7f ff 0d 10 32 t=25187"
    zeroTemp = "93 01 4b 46 7f ff 0d 10 32 : crc=32 YES\n93 01 4b 46 7f ff 0d 10 32 t=0"
    noTemp = "93 01 4b 46 7f ff 0d 10 32 : crc=32 YES\n93 01 4b 46 7f ff 0d 10 32 t="
    invalidTemp = "93 01 4b 46 7f ff 0d 10 32 : crc=32 YES\n93 01 4b 46 7f ff 0d 10 32 t=dfhg"
    empty = ""
    name = "testSensorName"
    
    @classmethod
    def setUpClass(cls):
        loginit.initTestLogging()
        TempSensorTest.logger = logging.getLogger(__name__)
        
    @patch('os.path.isfile')
    def test_getDataC(self, osMock):
        osMock.return_value = True
        
        sensor = Ds18b20(TempSensorTest.name, 'C', "/file")
        openMock = mock_open(read_data=TempSensorTest.goodData)
        with patch('__builtin__.open', openMock) as mockFile:
            self.assertEqual(sensor.getData(), 25.187)
            
    @patch('os.path.isfile')
    def test_getDataF(self, osMock):
        osMock.return_value = True
        
        sensor = Ds18b20(TempSensorTest.name, 'F', "/file")
        openMock = mock_open(read_data=TempSensorTest.goodData)
        with patch('__builtin__.open', openMock) as mockFile:
            self.assertEqual(sensor.getData(), 77.3366)
            
    @patch('os.path.isfile')
    def test_getDataBad(self, osMock):
        osMock.return_value = True
        
        sensor = Ds18b20(TempSensorTest.name, 'Q', "/file")
        openMock = mock_open(read_data=TempSensorTest.goodData)
        with patch('__builtin__.open', openMock) as mockFile:
            with self.assertRaises(ValueError):
                sensor.getData()