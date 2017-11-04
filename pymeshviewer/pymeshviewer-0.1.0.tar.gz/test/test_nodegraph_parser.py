import os
import unittest

from pymeshviewer.parser import parse_graph_json


class NodegraphParserTest(unittest.TestCase):
    def setUp(self):
        """
        Initialize Tests
        """

        file = open(
            os.path.dirname(os.path.realpath(__file__)) + os.sep + "testfiles/yanic_example_town_graph.json", "r")
        self.file_content = file.read()
        self.community = parse_graph_json(self.file_content)
        file.close()

    def test_version(self):
        """
        Test nodelist graph json version
        """
        self.assertEqual(self.community.version, 1)

    def test_batadv_directed(self):
        """
        Test nodelist graph batadv directed
        """
        self.assertEqual(self.community.protocol.directed, False)

    def test_batadv_graph(self):
        """
        Test nodelist graph batadv graph
        """
        self.assertEqual(self.community.protocol.graph, None)

    def test_batadv_nodes_size(self):
        """
        Test nodelist graph batadv nodelist count
        """
        self.assertEqual(len(self.community.protocol.nodes), 4)

    def test_batadv_links_size(self):
        """
        Test nodelist graph batadv link count
        """
        self.assertEqual(len(self.community.protocol.links), 3)

    def test_batadv_nodes(self):
        """
        Test batadv nodelist graph nodes value
        """
        self.assertEqual(self.community.protocol.nodes[0].node_id, "daff61000302")
        self.assertEqual(self.community.protocol.nodes[0].id, "da:ff:61:00:03:02")
        self.assertEqual(self.community.protocol.nodes[1].node_id, "daff61000402")
        self.assertEqual(self.community.protocol.nodes[1].id, "da:ff:61:00:04:02")

    def test_batadv_links(self):
        """
        Test batadv nodelist graph links value
        """
        self.assertEqual(self.community.protocol.links[0].source.node_id, "daff61000302")
        self.assertEqual(self.community.protocol.links[0].target.node_id, "daff61000402")
        self.assertEqual(self.community.protocol.links[0].vpn, False)
        self.assertEqual(self.community.protocol.links[0].tq, 1)
        self.assertEqual(self.community.protocol.links[0].bidirect, True)
