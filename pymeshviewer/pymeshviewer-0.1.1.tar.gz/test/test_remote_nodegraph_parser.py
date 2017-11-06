import unittest

import requests
from pymeshviewer.parser import parse_graph_json


class NodeGraphParserRemoteTest(unittest.TestCase):
    def test_darmstadt(self):
        json = requests.get("https://meshviewer.darmstadt.freifunk.net/data/ffda/graph.json").text
        self.graph_json = parse_graph_json(json)
