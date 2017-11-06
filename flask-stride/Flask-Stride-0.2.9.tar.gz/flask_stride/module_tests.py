import unittest
from .module import Module

class ModuleTests(unittest.TestCase):
    def test_add_property(self):
        """Test the add_property() method."""
        m = Module('module-key') 
        m.add_property('property_1', 'value_1')

        self.assertEqual(m.properties['property_1'], 'value_1')

    def test_to_descriptor(self):
        """Test the to_descriptor() method."""
        m = Module('module-key') 
        m.add_property('property_1', 'value_1')

        m_descriptor = m.to_descriptor()
        expected = {'key': 'module-key', 'property_1': 'value_1'}

        self.assertEqual(m.to_descriptor(), expected)

    def test_type(self):
        m = Module('module-key')
        self.assertEqual(m.type, None)

if __name__ == '__main__':
    unittest.main()
