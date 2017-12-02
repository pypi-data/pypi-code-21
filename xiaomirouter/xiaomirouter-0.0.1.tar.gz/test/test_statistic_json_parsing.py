import json
import unittest

from xiaomirouter.client import create_statistic_from_json


class JsonStatisticParsingTest(unittest.TestCase):
    def test_statistic_json_parsing(self):
        json_string = '{ "downspeed":"0", "online":"256367", "upspeed":"0" } '
        client = create_statistic_from_json(json.loads(json_string))
        self.assertEqual(client.get_downspeed(), "0")
        self.assertEqual(client.get_online(), "256367")
        self.assertEqual(client.get_upspeed(), "0")


if __name__ == '__main__':
    unittest.main()
