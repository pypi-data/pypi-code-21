import json
import unittest

from xiaomirouter.client import create_authority_from_json


class JsonAuthorityParsingTest(unittest.TestCase):
    def test_authority_json_parsing(self):
        json_string = '{ "wan":1, "pridisk":0, "admin":1, "lan":0 }'
        authority = create_authority_from_json(json.loads(json_string))
        self.assertEqual(authority.get_wan(), 1)
        self.assertEqual(authority.get_pridisk(), 0)
        self.assertEqual(authority.get_admin(), 1)
        self.assertEqual(authority.get_lan(), 0)


if __name__ == '__main__':
    unittest.main()
