# coding=utf-8
from tests.base import BaseTest
from mali_commands.utilities.tables import format_json_data


class TestTables(BaseTest):

    def testFormatJsonData_formatSpecifiedField(self):
        json_data = [
            {
                'a': 3,
                'b': 5,
            }
        ]

        formatters = {
            'a': lambda x: x * x
        }

        formatted_data = format_json_data(json_data, formatters=formatters)

        row = formatted_data[0]
        self.assertEqual(row['a'], 9)
        self.assertEqual(row['b'], 5)

    def testFormatJsonData_ignoreNonExistentField(self):
        json_data = [
            {
                'a': 3,
                'b': 5,
            }
        ]

        formatters = {
            'c': lambda x: x * x
        }

        formatted_data = format_json_data(json_data, formatters=formatters)
        self.assertEqual(formatted_data, json_data)
