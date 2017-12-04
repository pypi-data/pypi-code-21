import unittest
from .chatmessageaction import ChatMessageAction

class ChatMessageActionTests(unittest.TestCase):
    def test_init(self):
        """Test the __init__() method."""
        cma = ChatMessageAction(key='msg-act-key', name='Do Stuff', target='my-target-module')

        cma_descriptor = cma.to_descriptor()
        expected = {'key': 'msg-act-key', 'name': {'value':'Do Stuff'}, 'target': 'my-target-module'}

        self.assertEqual(cma_descriptor, expected)

if __name__ == '__main__':
    unittest.main()
