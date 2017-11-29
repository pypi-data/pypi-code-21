import unittest
from .chatbot import ChatBot

class ChatBotTests(unittest.TestCase):
    def test_init(self):
        """Test the __init__() method."""
        cb = ChatBot('chatbot-key', '/mention-path', '/dm-path')

        cb_descriptor = cb.to_descriptor()
        expected = {'key': 'chatbot-key', 'mention': {'url': '/mention-path'}, 'directMessage': {'url': '/dm-path'}}

        self.assertEqual(cb_descriptor, expected)

if __name__ == '__main__':
    unittest.main()
