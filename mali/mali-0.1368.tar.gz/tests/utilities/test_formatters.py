# coding=utf-8
from tests.base import BaseTest
from mali_commands.utilities.formatters import format_datetime, create_text_truncator


class TestFormatters(BaseTest):

    def testFormatDatetime(self):
        server_datetime = '2017-05-04T14:18:47.620155'
        formatted_datetime = format_datetime(server_datetime)
        self.assertEqual(formatted_datetime, 'May 04, 14:18')

    def testCreateTextTruncator_truncateLongText(self):
        max_length = 7
        text = BaseTest.some_random_shit(size=10)
        truncated_text = create_text_truncator(max_length)(text)

        self.assertEqual(truncated_text, text[:max_length] + '...')

    def testCreateTextTruncator_compressTo1LineText(self):
        text = 'abc\ndef\n'
        truncated_text = create_text_truncator(len(text))(text)

        self.assertEqual(truncated_text, 'abc def')
