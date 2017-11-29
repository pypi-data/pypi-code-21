import unittest
from .chatbotmessage import ChatBotMessage

class ChatBotMessageTests(unittest.TestCase):
    def test_init(self):
        """Test the __init__() method."""
        cbm = ChatBotMessage('chatbotmsg-key', 'hello.*', '/cb-msg')

        cbm_descriptor = cbm.to_descriptor()
        expected = {'key': 'chatbotmsg-key', 'pattern': 'hello.*', 'url': '/cb-msg'}

        self.assertEqual(cbm_descriptor, expected)

if __name__ == '__main__':
    unittest.main()
