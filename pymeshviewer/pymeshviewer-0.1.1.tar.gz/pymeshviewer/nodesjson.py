from datetime import datetime
from typing import List

from pymeshviewer import Protocol
from pymeshviewer.graph import NodeGraph
from pymeshviewer.node import Neighbour, Node
from pymeshviewer.nodecollection import NodeCollection


class NodesJSON(NodeCollection):
    def __init__(self, nodes: List[Node], version: int, timestamp: datetime):
        """
        Constructor for a Nodelist
        :param nodes: list of nodes
        :param version: format revision
        :param timestamp: timestamp of nodelist
        """
        super().__init__(nodes)
        self.nodes = nodes
        self.version = version
        self.timestamp = None
        if timestamp is not None:
            self.timestamp = datetime.now()


    def load_nodegraph(self, graph: NodeGraph):
        """
        Loads nodegraph into nodelist and adds neighbours to nodes
        :param graph: corresponding nodegraph for nodelist
        """
        links = graph.protocol.links
        for link in links:
            source = self.get_node(link.source.node_id)
            target = self.get_node(link.target.node_id)
            if source and target:
                source.neighbours.append(
                    Neighbour(Protocol.BATMAN_ADV, target.nodeinfo.node_id, link.vpn,
                              int((float(2) - float(link.tq)) * 100),
                              link.bidirect))
                target.neighbours.append(
                    Neighbour(Protocol.BATMAN_ADV, source.nodeinfo.node_id, link.vpn,
                              int((float(2) - float(link.tq)) * 100),
                              link.bidirect))
