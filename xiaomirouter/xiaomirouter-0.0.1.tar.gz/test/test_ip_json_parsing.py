import json
import unittest

from xiaomirouter.client import create_ip_from_json


class JsonIPParsingTest(unittest.TestCase):
    def test_ip_json_parsing(self):
        json_string = '{ "downspeed":"0", "online":"256367", "active":1, ' \
                      '"upspeed":"0", "ip":"192.168.0.111" } '
        client = create_ip_from_json(json.loads(json_string))
        self.assertEqual(client.get_downspeed(), "0")
        self.assertEqual(client.get_online(), "256367")
        self.assertEqual(client.get_active(), 1)
        self.assertEqual(client.get_upspeed(), "0")
        self.assertEqual(client.get_ip(), "192.168.0.111")


if __name__ == '__main__':
    unittest.main()
