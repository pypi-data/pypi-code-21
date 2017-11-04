import os
import unittest

from pymeshviewer.parser import parse_meshviewer_json


class NodecollectionTest(unittest.TestCase):
    def setUp(self):
        """
        Initialize Tests
        """
        nodelist_file = open(
            os.path.dirname(os.path.realpath(__file__)) + os.sep + "testfiles/yanic_example_town_meshviewer.json", "r")
        self.meshviewer_json = parse_meshviewer_json(nodelist_file.read())
        nodelist_file.close()

    def test_closest_node(self):
        """ Assert that closest node is returned """
        node, distance = self.meshviewer_json.get_closest_node(49.835076144, 8.697116375)
        self.assertEqual(node, self.meshviewer_json.get_node("c04a00dd692a"))
        self.assertAlmostEqual(distance, 0.304, 3)
