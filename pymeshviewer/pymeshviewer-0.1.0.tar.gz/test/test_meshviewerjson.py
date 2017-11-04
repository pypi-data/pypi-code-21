import os
import unittest

from pymeshviewer.parser import parse_meshviewer_json


class MeshviewerJsonTest(unittest.TestCase):
    def setUp(self):
        nodelist_file = open(
            os.path.dirname(os.path.realpath(__file__)) + os.sep + "testfiles/yanic_example_town_meshviewer.json", "r")
        self.meshviewer_json = parse_meshviewer_json(nodelist_file.read())
        nodelist_file.close()

    def test_get_node(self):
        """
        Verify that get_node() returns the correct node
        """
        self.assertEqual(self.meshviewer_json.get_node("daff61000302"), self.meshviewer_json.nodes[0])
        self.assertEqual(self.meshviewer_json.get_node("daff61000402"), self.meshviewer_json.nodes[1])
        self.assertEqual(self.meshviewer_json.get_node("c04a00dd692a"), self.meshviewer_json.nodes[2])
        self.assertEqual(self.meshviewer_json.get_node("60e3272f92b2"), self.meshviewer_json.nodes[3])
        self.assertIsNone(self.meshviewer_json.get_node("000000000000"))

    def test_enabled_vpn_nodes(self):
        """
        Verify correct return value for vpn enabled nodes
        """
        self.assertEqual(len(self.meshviewer_json.vpn_enabled), 0)

    def test_established_vpn_nodes(self):
        """
        Verify correct return value for vpn established nodes
        """
        self.assertEqual(len(self.meshviewer_json.established_vpn_connection), 1)

    def test_model_stats(self):
        """
        Verify correct return value for model stats
        """
        self.assertDictEqual(self.meshviewer_json.model_stats, {'TP-Link TL-WDR3600 v1': 1, 'TP-Link Archer C7 v2': 1})
