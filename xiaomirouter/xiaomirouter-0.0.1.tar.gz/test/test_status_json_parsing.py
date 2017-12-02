import json
import unittest

from xiaomirouter.status import create_status_from_json


class StatusJsonParsingTest(unittest.TestCase):
    def test_status_json_parsing(self):
        json_string = \
            '{"dev":[{"mac":"AA:BB:CC:DD:EE:FF","maxdownloadspeed":"1314712",' \
            '"upload":"373225059","upspeed":"143","downspeed":"191",' \
            '"online":"272518","devname":"Chromecast",' \
            '"maxuploadspeed":"212407","download":"6327018672"},' \
            '{"mac":"FF:EE:DD:CC:BB:AA","maxdownloadspeed":"10739932",' \
            '"upload":"74005799","upspeed":"0","downspeed":"0",' \
            '"online":"162439","devname":"Computer",' \
            '"maxuploadspeed":"190451","download":"3352994518"}],"code":0,' \
            '"mem":{"usage":0.36,"total":"128 M","hz":"800MHz",' \
            '"type":"DDR2"},"temperature":0,"count":{"all":90,"online":9},' \
            '"hardware":{"mac":"00:11:22:33:44:55","platform":"R1CM",' \
            '"version":"2.8.91","channel":"release","sn":"11380/00012345"},' \
            '"upTime":"272721.33","cpu":{"core":1,"hz":"580MHz",' \
            '"load":0.0634},"wan":{"downspeed":"10812",' \
            '"maxdownloadspeed":"12489843","history":"51396,35252,21064,' \
            '29924,18030,19505,40936,19910,16504,262308,19474,21111",' \
            '"devname":"eth0.2","upload":"6838942104","upspeed":"10299",' \
            '"maxuploadspeed":"1262341","download":"49992630560"}} '
        status = create_status_from_json(json.loads(json_string))
        devs = status.get_dev()
        dev = devs[0]
        self.assertEqual(dev.get_mac(), "AA:BB:CC:DD:EE:FF")
        self.assertEqual(dev.get_maxdownloadspeed(), "1314712")
        self.assertEqual(dev.get_upload(), "373225059")
        self.assertEqual(dev.get_upspeed(), "143")
        self.assertEqual(dev.get_downspeed(), "191")
        self.assertEqual(dev.get_online(), "272518")
        self.assertEqual(dev.get_devname(), "Chromecast")
        self.assertEqual(dev.get_maxuploadspeed(), "212407")
        self.assertEqual(dev.get_download(), "6327018672")
        self.assertEqual(status.get_code(), 0)
        mem = status.get_mem()
        self.assertEqual(mem.get_usage(), 0.36)
        self.assertEqual(mem.get_total(), "128 M")
        self.assertEqual(mem.get_hz(), "800MHz")
        self.assertEqual(mem.get_type(), "DDR2")
        self.assertEqual(status.get_temperature(), 0)
        count = status.get_count()
        self.assertEqual(count.get_all(), 90)
        self.assertEqual(count.get_online(), 9)
        hardware = status.get_hardware()
        self.assertEqual(hardware.get_mac(), "00:11:22:33:44:55")
        self.assertEqual(hardware.get_platform(), "R1CM")
        self.assertEqual(hardware.get_version(), "2.8.91")
        self.assertEqual(hardware.get_channel(), "release")
        self.assertEqual(hardware.get_sn(), "11380/00012345")
        self.assertEqual(status.get_up_time(), "272721.33")
        cpu = status.get_cpu()
        self.assertEqual(cpu.get_core(), 1)
        self.assertEqual(cpu.get_hz(), "580MHz")
        self.assertEqual(cpu.get_load(), 0.0634)
        wan = status.get_wan()
        self.assertEqual(wan.get_downspeed(), "10812")
        self.assertEqual(wan.get_maxdownloadspeed(), "12489843")
        self.assertEqual(wan.get_history(),
                         "51396,35252,21064,29924,18030,19505,40936,19910,16504,262308,19474,21111")
        self.assertEqual(wan.get_devname(), "eth0.2")
        self.assertEqual(wan.get_upload(), "6838942104")
        self.assertEqual(wan.get_upspeed(), "10299")
        self.assertEqual(wan.get_maxuploadspeed(), "1262341")
        self.assertEqual(wan.get_download(), "49992630560")


if __name__ == '__main__':
    unittest.main()
