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

    def test_online_nodes(self):
        """ Asserts that all offline nodes are returned """
        self.assertEqual(len(self.meshviewer_json.online), 4)

    def test_offline_nodes(self):
        self.assertEqual(len(self.meshviewer_json.offline), 0)

    def test_get_hostname(self):
        self.assertEqual(len(self.meshviewer_json.get_hostname("invalid")), 0)
        self.assertEqual(self.meshviewer_json.get_hostname("e"),
                         [self.meshviewer_json.get_node("60e3272f92b2"),
                          self.meshviewer_json.get_node("c04a00dd692a"),
                          self.meshviewer_json.get_node("daff61000302"),
                          self.meshviewer_json.get_node("daff61000402")])  # Check sorting
        self.assertEqual(self.meshviewer_json.get_hostname("tagungshotel"),
                         [self.meshviewer_json.get_node("60e3272f92b2")])
        self.assertEqual(self.meshviewer_json.get_hostname("64367-tagungshotel02"),
                         [self.meshviewer_json.get_node("60e3272f92b2")])
        self.assertEqual(self.meshviewer_json.get_hostname("64367-tagungshotel02 "), [])
        self.assertEqual(self.meshviewer_json.get_hostname("block"), [self.meshviewer_json.get_node("c04a00dd692a")])
