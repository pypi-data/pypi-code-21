import unittest
from .chataction import ChatAction

class ChatActionTests(unittest.TestCase):
    def test_init(self):
        """Test the __init__() method."""
        ca = ChatAction(key='act-key', name='Do Stuff', target='my-target-module')

        ca_descriptor = ca.to_descriptor()
        expected = {'key': 'act-key', 'name': {'value':'Do Stuff'}, 'target': 'my-target-module'}

        self.assertEqual(ca_descriptor, expected)

if __name__ == '__main__':
    unittest.main()
