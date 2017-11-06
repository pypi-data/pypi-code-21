import unittest

import requests
from pymeshviewer.parser import parse_nodes_json


class NodesJsonParserRemoteTest(unittest.TestCase):
    def test_darmstadt(self):
        json = requests.get("https://meshviewer.darmstadt.freifunk.net/data/ffda/nodes.json").text
        self.node_json = parse_nodes_json(json)
