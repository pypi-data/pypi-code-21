import unittest

import httpretty

from xiaomirouter import XiaomiRouter


class ClientCommunicationTest(unittest.TestCase):

    @httpretty.activate
    def test_device_list_retrieval(self):
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

        get_device_list_answer = \
            '{"mac":"AA:BB:CC:DD:EE:FF","list":[{"mac":"AA:BB:CC:DD:EE:FF",' \
            '"oname":"OrangeTVKey","isap":0,"parent":"","authority":{"wan":1,' \
            '"pridisk":0,"admin":1,"lan":0},"push":0,"online":1,' \
            '"name":"OrangeTVKey","times":0,"ip":[{"downspeed":"0",' \
            '"online":"256367","active":1,"upspeed":"0",' \
            '"ip":"192.168.0.111"}],"statistics":{"downspeed":"0",' \
            '"online":"256367","upspeed":"0"},"icon":"","type":1},' \
            '{"mac":"AA:BB:CC:DD:EE:FF","oname":"hpgen8","isap":0,' \
            '"parent":"","authority":{"wan":1,"pridisk":0,"admin":1,"lan":0},' \
            '"push":0,"online":1,"name":"HP Gen8","times":0,"ip":[{' \
            '"downspeed":"25","online":"256191","active":1,"upspeed":"60",' \
            '"ip":"192.168.0.112"}],"statistics":{"downspeed":"25",' \
            '"online":"256191","upspeed":"60"},"icon":"","type":0},' \
            '{"mac":"AA:BB:CC:DD:EE:FF","oname":"Google-Home","isap":0,' \
            '"parent":"AA:BB:CC:DD:EE:FF","authority":{"wan":1,"pridisk":0,' \
            '"admin":1,"lan":0},"push":0,"online":1,"name":"Google-Home",' \
            '"times":0,"ip":[{"downspeed":"0","online":"256367","active":1,' \
            '"upspeed":"60","ip":"192.168.0.48"}],"statistics":{' \
            '"downspeed":"0","online":"256367","upspeed":"60"},"icon":"",' \
            '"type":1}],"code":0} '
        httpretty.register_uri(httpretty.GET,
                               "http://192.168.12.255/cgi-bin/luci/;stok"
                               "=2ba9a16cd4771fa11ba7ba6ebe46e337/api"
                               "/misystem/devicelist", get_device_list_answer)
        client_list = router_object.retrieve_client_list()
        self.assertEqual(len(client_list), 3)


if __name__ == '__main__':
    unittest.main()
