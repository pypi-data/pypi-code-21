import unittest

import os

from pymeshviewer.parser.graph import parse_graph_json


class NodelistParserTest(unittest.TestCase):
    def setUp(self):
        """
        Initialize Tests
        """
        self.file_content = {}
        self.communities = {}

        darmstadt_file = open(os.path.dirname(os.path.realpath(__file__)) + os.sep + "testfiles/yanic_darmstadt_graph.json", "r")
        self.file_content["darmstadt"] = darmstadt_file.read()
        self.communities["darmstadt"] = parse_graph_json(self.file_content["darmstadt"])
        darmstadt_file.close()

    def test_version(self):
        """
        Test nodelist graph json version
        """
        self.assertEqual(self.communities["darmstadt"].version, 1)

    def test_batadv_directed(self):
        """
        Test nodelist graph batadv directed
        """
        self.assertEqual(self.communities["darmstadt"].protocol.directed, False)

    def test_batadv_graph(self):
        """
        Test nodelist graph batadv graph
        """
        self.assertEqual(self.communities["darmstadt"].protocol.graph, None)

    def test_batadv_nodes_size(self):
        """
        Test nodelist graph batadv nodelist count
        """
        self.assertEqual(len(self.communities["darmstadt"].protocol.nodes), 687)

    def test_batadv_links_size(self):
        """
        Test nodelist graph batadv link count
        """
        self.assertEqual(len(self.communities["darmstadt"].protocol.links), 1107)

    def test_batadv_nodes(self):
        """
        Test batadv nodelist graph nodes value
        """
        self.assertEqual(self.communities["darmstadt"].protocol.nodes[0].node_id, "64700277e886")
        self.assertEqual(self.communities["darmstadt"].protocol.nodes[0].id, "64:70:02:77:e8:86")
        self.assertEqual(self.communities["darmstadt"].protocol.nodes[1].node_id, "60e3272f982e")
        self.assertEqual(self.communities["darmstadt"].protocol.nodes[1].id, "60:e3:27:2f:98:2e")

    def test_batadv_links(self):
        """
        Test batadv nodelist graph links value
        """
        self.assertEqual(self.communities["darmstadt"].protocol.links[0].source.node_id, "64700277e886")
        self.assertEqual(self.communities["darmstadt"].protocol.links[0].target.node_id, "60e3272f982e")
        self.assertEqual(self.communities["darmstadt"].protocol.links[0].vpn, False)
        self.assertEqual(self.communities["darmstadt"].protocol.links[0].tq, 1)
        self.assertEqual(self.communities["darmstadt"].protocol.links[0].bidirect, True)
