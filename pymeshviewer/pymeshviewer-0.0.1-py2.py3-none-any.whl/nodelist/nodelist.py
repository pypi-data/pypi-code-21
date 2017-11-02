from datetime import datetime
from typing import List, Dict, Optional

from pymeshviewer import Protocol
from pymeshviewer.graph import NodeGraph
from pymeshviewer.nodelist.node import Neighbour, Node


class Nodelist:
    def __init__(self, nodes: List[Node], version: int, timestamp: datetime):
        """
        Constructor for a Nodelist
        :param nodes: list of nodes
        :param version: format revision
        :param timestamp: timestamp of nodelist
        """
        self.nodes = nodes
        self.version = version
        self.timestamp = None
        if timestamp is not None:
            self.timestamp = datetime.now()

    @property
    def node_count(self) -> int:
        """
        Total number of nodes in nodelist
        :return: total number of nodes in nodelist
        """
        return len(self.nodes)

    @property
    def models(self) -> Dict[str, Node]:
        """
        Nodes by their models
        :return: nodes ordered by model
        """
        models = {}
        for node in self.nodes:
            if node.nodeinfo.hardware.model not in models:
                models[node.nodeinfo.hardware.model] = []
            models[node.nodeinfo.hardware.model].append(node)
        return models

    @property
    def vpn_enabled(self):
        """
        Nodes with enabled vpn
        :return: nodes with enabled vpn
        """
        nodes = []
        for node in self.nodes:
            if node.nodeinfo.software.fastd.enabled is True:
                nodes.append(node)
        return nodes

    @property
    def established_vpn_connection(self) -> List[Node]:
        """
        Nodes with established vpn connection
        :return: nodes with established vpn connection
        """
        nodes = []
        for node in self.vpn_enabled:
            if node.vpn_active:
                nodes.append(node)
        return nodes

    @property
    def model_stats(self) -> Dict[str, int]:
        """
        Models and their quantity
        :return: models and their quantity
        """
        models = {}
        for node in self.nodes:
            model = node.nodeinfo.hardware.model
            if model is None:
                continue
            if model not in models:
                models[model] = 0
            models[model] += 1
        return models

    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Returns node identified by its node_id
        :param node_id: node_id of desired node
        :return: Node if node present in nodelist, None otherwise
        """
        for node in self.nodes:
            if node.nodeinfo.node_id == node_id:
                return node
        return None

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
