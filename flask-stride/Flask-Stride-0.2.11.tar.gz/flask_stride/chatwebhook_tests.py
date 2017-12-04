import unittest
from .chatwebhook import ChatWebhook

class ChatWebhookTests(unittest.TestCase):
    def test_init(self):
        """Test the __init__() method."""
        wh = ChatWebhook(key='webhook-key', event='conversation:updates', url='https://my-external-service.com/stride-webhooks')

        wh_descriptor = wh.to_descriptor()
        expected = {'key': 'webhook-key', 'event': 'conversation:updates', 'url': 'https://my-external-service.com/stride-webhooks'}

        self.assertEqual(wh_descriptor, expected)

if __name__ == '__main__':
    unittest.main()
