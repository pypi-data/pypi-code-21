import unittest
from .chatinputaction import ChatInputAction

class ChatInputActionTests(unittest.TestCase):
    def test_init(self):
        """Test the __init__() method."""
        cia = ChatInputAction(key='inp-act-key', name='Do Stuff', target='my-target-module')

        cia_descriptor = cia.to_descriptor()
        expected = {'key': 'inp-act-key', 'name': {'value':'Do Stuff'}, 'target': 'my-target-module'}

        self.assertEqual(cia_descriptor, expected)

if __name__ == '__main__':
    unittest.main()
