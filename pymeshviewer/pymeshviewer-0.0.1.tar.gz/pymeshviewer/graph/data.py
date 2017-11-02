from pymeshviewer import Protocol


class Node:
    def __init__(self, id=None, node_id=None):
        self.id = id
        self.node_id = node_id


class Link:
    def __init__(self, source: str = None, target: str = None, vpn: bool = False, tq: int = 0, bidirect: bool = False):
        self.source = source
        self.target = target
        self.vpn = vpn
        self.tq = tq
        self.bidirect = bidirect


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
    def __init__(self, version: int = 0, protocol: ProtocolBatmanAdv = ProtocolBatmanAdv(), protocol_type: Protocol = None):
        self.version = version
        self.protocol = protocol
        self.protocol_type = protocol_type
