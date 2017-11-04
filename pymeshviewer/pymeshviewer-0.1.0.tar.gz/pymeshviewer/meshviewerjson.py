from datetime import datetime
from typing import List

from pymeshviewer.graph import Link
from pymeshviewer.node import Node
from pymeshviewer.nodecollection import NodeCollection


class MeshviewerJSON(NodeCollection):
    def __init__(self, timestamp: datetime, nodes: List[Node], links: List[Link]):
        """
        Constructor for a MeshviewerJSON object
        :param timestamp: timestamp of MeshviewerJSON
        :param nodes: list of nodes
        :param links: list of links
        """
        super().__init__(nodes)
        self.timestamp = timestamp
        self.nodes = nodes
        self.links = links
