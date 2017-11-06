import unittest

import requests
from pymeshviewer.parser import parse_meshviewer_json


class MeshviewerJsonParserRemoteTest(unittest.TestCase):
    def test_darmstadt(self):
        json = requests.get("https://meshviewer.darmstadt.freifunk.net/data/ffda/meshviewer.json").text
        self.meshviewer_json = parse_meshviewer_json(json)

    def test_bremen(self):
        json = requests.get("https://downloads.bremen.freifunk.net/data/meshviewer.json").text
        self.meshviewer_json = parse_meshviewer_json(json)
