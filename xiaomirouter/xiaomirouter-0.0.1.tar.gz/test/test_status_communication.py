import unittest

import httpretty

from xiaomirouter import XiaomiRouter


class StatusCommunicationTest(unittest.TestCase):

    @httpretty.activate
    def test_status_retrieval(self):
        httpretty.register_uri(httpretty.POST, "http://192.168.12.255/cgi-bin"
                                               "/luci/api/xqsystem/login",
                               body='{"url":"/cgi-bin/luci/;stok'
                                    '=2ba9a16cd4771fa11ba7ba6ebe46e337/web'
                                    '/home",'
                                    '"token'
                                    '":"2ba9a16cd4771fa11ba7ba6ebe46e337",'
                                    '"code":0}')
        router_object = XiaomiRouter("192.168.12.255", "passtest")

        self.assertTrue(router_object.is_successfully_initialised())

        get_status_answer = \
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
        httpretty.register_uri(httpretty.GET,
                               "http://192.168.12.255/cgi-bin/luci/;stok"
                               "=2ba9a16cd4771fa11ba7ba6ebe46e337/api"
                               "/misystem/status", get_status_answer)
        status_info = router_object.retrieve_status_info()
        self.assertEqual(status_info.get_up_time(), "272721.33")


if __name__ == '__main__':
    unittest.main()
