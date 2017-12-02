import json
import unittest

from xiaomirouter import create_client_from_json


class JsonParsingTest(unittest.TestCase):
    def test_client_json_parsing(self):
        json_string = \
            '{ "mac":"AA:BB:CC:DD:EE:FF", "oname":"oname1", "isap":0, ' \
            '"parent":"", "authority":{ "wan":1, "pridisk":0, "admin":1, ' \
            '"lan":0 }, "push":0, "online":1, "name":"nameABC", "times":0, ' \
            '"ip":[ { "downspeed":"0", "online":"256367", "active":1, ' \
            '"upspeed":"0", "ip":"192.168.0.111" } ], "statistics":{ ' \
            '"downspeed":"0", "online":"256367", "upspeed":"0" }, ' \
            '"icon":"", "type":1 } '
        client = create_client_from_json(json.loads(json_string))
        self.assertEqual(client.get_mac(), "AA:BB:CC:DD:EE:FF")
        self.assertEqual(client.get_original_name(), "oname1")
        self.assertEqual(client.get_isap(), 0)
        self.assertEqual(client.get_parent(), "")
        self.assertIsNotNone(client.get_authority())
        authority = client.get_authority()
        self.assertEqual(authority.get_wan(), 1)
        self.assertEqual(client.get_push(), 0)
        self.assertEqual(client.get_online(), 1)
        self.assertEqual(client.get_name(), "nameABC")
        self.assertEqual(client.get_times(), 0)
        ips = client.get_ips()
        self.assertIsNotNone(ips)
        self.assertEqual(len(ips), 1)
        ip = ips[0]
        self.assertEqual(ip.get_ip(), "192.168.0.111")
        statistics = client.get_statistics()
        self.assertEqual(statistics.get_online(), "256367")
        self.assertEqual(client.get_type(), 1)


if __name__ == '__main__':
    unittest.main()
