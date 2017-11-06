from typing import Dict, Optional, List, Tuple

from pymeshviewer.node import Node
from pymeshviewer.util import calculate_distance


class NodeCollection:
    def __init__(self, nodes: List[Node]):
        self.nodes = nodes

    @property
    def node_count(self) -> int:
        """
        Total number of nodes in nodelist
        :return: total number of nodes in nodelist
        """
        return len(self.nodes)

    @property
    def online(self) -> List[Node]:
        return [n for n in self.nodes if n.online]

    @property
    def offline(self) -> List[Node]:
        return [n for n in self.nodes if not n.online]

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
            if node.vpn_enabled is True:
                nodes.append(node)
        return nodes

    @property
    def established_vpn_connection(self) -> List[Node]:
        """
        Nodes with established vpn connection
        :return: nodes with established vpn connection
        """
        nodes = []
        for node in self.nodes:
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

    def get_closest_node(self, latitude, longitude, online=None) -> Tuple[Node, float]:
        """
        Returns the closest node and the distance relative to provided coordinates
        :param latitude: latitude
        :param longitude: longitude
        :param online: indicates if the closest online/offline node is looked for, ignores status if unset
        :return: tuple consisting of closest node and distance in km
        """
        if online is None:
            nodes = self.nodes
        elif online is True:
            nodes = self.online
        elif online is False:
            node = self.offline

        closest = None
        closest_distance = None
        for node in self.nodes:
            if node.nodeinfo.location is None:
                continue
            distance = calculate_distance(latitude, longitude, node.nodeinfo.location.latitude,
                                          node.nodeinfo.location.longitude)
            if closest_distance is None or closest_distance > distance:
                closest_distance = distance
                closest = node

        return closest, closest_distance

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

    def get_hostname(self, hostname: str) -> List[Node]:
        """
        Returns all nodes which hostname contain a specified string as a List
        :param hostname: hostname of desired node(s)
        :return: list of nodes with specified hostname
        """
        nodes = [n for n in self.nodes if hostname in n.nodeinfo.hostname]
        sorted_x = sorted(nodes,
                          key=lambda n: len(n.nodeinfo.hostname) - len(hostname) * n.nodeinfo.hostname.count(hostname))
        return sorted_x
