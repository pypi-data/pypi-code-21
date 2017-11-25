# pylint: disable=C0103

import unittest
import logging

from unicornclient import parser
from unicornclient import message

class ParserTest(unittest.TestCase):
    def setUp(self):
        my_message = message.Message()
        my_message.set_header({'message':'hello world'})
        my_message.set_body(b'1234567890')
        self.my_message = my_message

        message1 = message.Message()
        message1.set_header({'message':'hello world 1'})
        message1.set_body(b'1111')
        self.message1 = message1

        message2 = message.Message()
        message2.set_header({'message':'hello world 2'})
        message2.set_body(b'2222')
        self.message2 = message2

    def test_one_message(self):
        my_parser = parser.Parser()
        my_parser.feed(self.my_message.encode())
        parsed = my_parser.parse_one()

        self.assertEqual(parsed.header, self.my_message.header)
        self.assertEqual(parsed.body, self.my_message.body)

    def test_one_message_with_remaining(self):
        my_parser = parser.Parser()
        extra_data = b'112233445566'
        my_parser.feed(self.my_message.encode() + extra_data)
        parsed = my_parser.parse_one()

        self.assertEqual(parsed.header, self.my_message.header)
        self.assertEqual(parsed.body, self.my_message.body)
        self.assertEqual(my_parser.remaining, extra_data)

    def test_split_message(self):
        my_parser = parser.Parser()
        binary_string = self.my_message.encode()

        my_parser.feed(binary_string[:10])
        first_parsed = my_parser.parse_one()

        my_parser.feed(binary_string[10:])
        second_parsed = my_parser.parse_one()

        self.assertIsNone(first_parsed)
        self.assertEqual(second_parsed.header, self.my_message.header)
        self.assertEqual(second_parsed.body, self.my_message.body)

    def test_two_message(self):
        my_parser = parser.Parser()
        my_parser.feed(self.message1.encode() + self.message2.encode())

        first_parsed = my_parser.parse_one()

        self.assertEqual(first_parsed.header, self.message1.header)
        self.assertEqual(first_parsed.body, self.message1.body)
        self.assertEqual(my_parser.remaining, self.message2.encode())

        second_parsed = my_parser.parse_one()

        self.assertEqual(second_parsed.header, self.message2.header)
        self.assertEqual(second_parsed.body, self.message2.body)
        self.assertEqual(my_parser.remaining, b'')

    def test_multi_message(self):
        my_parser = parser.Parser()

        message3 = message.Message()
        message3.set_header({'message':'hello world 3'})
        message3.set_body(b'3333')

        binary_string = message3.encode()
        data = self.message1.encode() + self.message2.encode() + binary_string[:10]
        my_parser.feed(data)
        parsed = my_parser.parse()

        self.assertEqual(len(parsed), 2)
        first_parsed = parsed[0]
        second_parsed = parsed[1]

        self.assertEqual(first_parsed.header, self.message1.header)
        self.assertEqual(first_parsed.body, self.message1.body)
        self.assertEqual(second_parsed.header, self.message2.header)
        self.assertEqual(second_parsed.body, self.message2.body)

    def test_bad_json_header(self):
        logging.disable(logging.CRITICAL)
        my_parser = parser.Parser()

        data = self.message1.encode() + self.message2.encode()
        data = data[:16] + b':' + data[17:]

        my_parser.feed(data)
        parsed = my_parser.parse()

        self.assertEqual(len(parsed), 2)
        first_parsed = parsed[0]
        second_parsed = parsed[1]

        self.assertIsNone(first_parsed.header)
        self.assertEqual(first_parsed.body, self.message1.body)
        self.assertEqual(second_parsed.header, self.message2.header)
        self.assertEqual(second_parsed.body, self.message2.body)

if __name__ == '__main__':
    unittest.main()
