from enum import Enum

from pymeshviewer import Protocol


class LinkType(Enum):
    OTHER = 0
    WIFI = 1
    VPN = 2


class Node:
    def __init__(self, id=None, node_id=None):
        self.id = id
        self.node_id = node_id


class Link:
    def __init__(self, source: str = None, target: str = None, link_type: LinkType = LinkType.OTHER, vpn: bool = False,
                 tq: int = None, source_tq: int = None, target_tq: int = None, bidirect: bool = False):
        self.source = source
        self.target = target
        self.link_type = link_type
        if vpn is True:
            self.link_type = LinkType.OTHER
        self.source_tq = source_tq
        self.target_tq = target_tq
        if tq and source_tq is None and target_tq is None:
            self.target_tq = tq
            self.source_tq = tq
            self.bidirect = False
        self.bidirect = bidirect

        if self.target_tq == 0:
            self.bidirect = False

    @property
    def tq(self):
        return (self.source_tq + self.target_tq) / 2

    @property
    def vpn(self):
        return self.link_type == LinkType.VPN


class ProtocolBatmanAdv:
    def __init__(self, directed: bool = False, graph=None, nodes: list = None, links: list = None):
        if links is None:
            links = []
        if nodes is None:
            nodes = []
        self.directed = directed
        self.graph = graph
        self.nodes = nodes
        self.links = links


class NodeGraph:
    def __init__(self, version: int = 0, protocol: ProtocolBatmanAdv = ProtocolBatmanAdv(),
                 protocol_type: Protocol = None):
        self.version = version
        self.protocol = protocol
        self.protocol_type = protocol_type
