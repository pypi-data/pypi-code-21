import os
import unittest

from pymeshviewer.parser import parse_nodes_json, parse_graph_json


class NodelistTest(unittest.TestCase):
    def setUp(self):
        """
        Initialize Tests
        """
        nodelist_file = open(
            os.path.dirname(os.path.realpath(__file__)) + os.sep + "testfiles/yanic_example_town_nodes.json", "r")
        self.nodelist = parse_nodes_json(nodelist_file.read())
        nodelist_file.close()

        nodegraph_file = open(
            os.path.dirname(os.path.realpath(__file__)) + os.sep + "testfiles/yanic_example_town_graph.json", "r")
        self.nodegraph = parse_graph_json(nodegraph_file.read())
        nodegraph_file.close()

    def test_get_node(self):
        """
        Verify that get_node() returns the correct node
        """
        self.assertEqual(self.nodelist.get_node("daff61000302"), self.nodelist.nodes[0])
        self.assertEqual(self.nodelist.get_node("daff61000402"), self.nodelist.nodes[1])
        self.assertEqual(self.nodelist.get_node("c04a00dd692a"), self.nodelist.nodes[2])
        self.assertEqual(self.nodelist.get_node("60e3272f92b2"), self.nodelist.nodes[3])
        self.assertIsNone(self.nodelist.get_node("000000000000"))

    def test_enabled_vpn_nodes(self):
        """
        Verify correct return value for vpn enabled nodes
        """
        self.assertEqual(len(self.nodelist.vpn_enabled), 3)

    def test_established_vpn_nodes(self):
        """
        Verify correct return value for vpn established nodes
        """
        self.assertEqual(len(self.nodelist.established_vpn_connection), 1)

    def test_model_stats(self):
        """
        Verify correct return value for model stats
        """
        self.assertDictEqual(self.nodelist.model_stats, {'TP-Link TL-WDR3600 v1': 1, 'TP-Link Archer C7 v2': 1})

    def test_load_nodegraph(self):
        """
        Test loading neighbours from Node Graph into nodelist
        """
        self.nodelist.load_nodegraph(self.nodegraph)

        self.assertEqual(len(self.nodelist.get_node("daff61000302").neighbours), 2)
