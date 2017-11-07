import unittest

from velenxc.parsers.json import JSONParser, JSONPathParser


class JSONTestCase(unittest.TestCase):
    def test_should_not_be_able_to_use_abstract_method(self):
        with self.failUnlessRaises(NotImplementedError):
            parser = JSONParser()
            parser.parse("{}", '')

    def test_should_handle_zip_type(self):
        parser = JSONPathParser()
        result = parser.parse({"name": "aaa"}, ['$.name', ], **{'parse_type': 'zip'})
        self.assertTrue(len(result['parse_values']) > 0)

    def test_should_handle_non_existing_json_path(self):
        parser = JSONPathParser()
        result = parser.parse({"name": "aaa"}, ['$.name', '$.other'])
        self.assertTrue(len(result['not_match_path']) > 0)

    def test_should_index_error_return_none(self):
        parser = JSONPathParser()
        result = parser.parse({"users": []}, ['$.users[0].age'])
        self.assertIsNone(result['parse_values'][0])
