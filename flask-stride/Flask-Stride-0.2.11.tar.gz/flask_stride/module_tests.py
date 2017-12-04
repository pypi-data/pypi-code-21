import unittest
from .module import Module

class ModuleTests(unittest.TestCase):
    def test_add_property(self):
        """Test the add_property() method."""
        m = Module('module-key') 
        m.add_property('property_1', 'value_1')

        self.assertIn('property_1', m.properties)
        self.assertEqual(m.properties['property_1'], 'value_1')

    def test_del_property(self):
        """Test the del_property() method."""
        m = Module('module-key')
        m.add_property('property_1', 'value_1')
        m.del_property('property_1')

        self.assertNotIn('property_1', m.properties)

    def test_to_descriptor(self):
        """Test the to_descriptor() method."""
        m = Module('module-key') 
        m.add_property('property_1', 'value_1')

        m_descriptor = m.to_descriptor()
        expected = {'key': 'module-key', 'property_1': 'value_1'}

        self.assertEqual(m.to_descriptor(), expected)

    def test__descriptor_value(self):
        """Test the _descriptor_value() method."""
        m = Module('module-key')
        m2 = Module('module-key-2')
        m2.add_property('m2-property-1', 'hello.')

        m.add_property('property_str', 'this is a string.')
        m.add_property('property_list', ['this', 'is', 'a', 'list'])
        m.add_property('property_dict', {'key': 'value'})
        m.add_property('property_mod', m2)

        m_descriptor = m.to_descriptor()
        expected = {'key': 'module-key', 'property_str': 'this is a string.', 'property_list': ['this', 'is', 'a', 'list'], 'property_dict':{'key': 'value'}, 'property_mod': {'key':'module-key-2','m2-property-1':'hello.'}}

        self.assertEqual(m.to_descriptor(), expected)

    def test_type(self):
        m = Module('module-key')
        self.assertEqual(m.type, None)

if __name__ == '__main__':
    unittest.main()
