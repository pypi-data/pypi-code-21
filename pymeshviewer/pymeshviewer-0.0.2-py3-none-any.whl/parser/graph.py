import json

from pymeshviewer import Protocol
from pymeshviewer.graph import Node, Link, NodeGraph, ProtocolBatmanAdv


def parse_graph_json(input_string: str) -> NodeGraph:
    """
    Parses the provided node graph json string and returns it as a NodeGraph object
    :param input_dict: node graph json string
    :return: a NodeGraph object containing the information from the input
    """
    return parse_node_graph(json.loads(input_string))


def parse_node_graph(input_dict: dict) -> NodeGraph:
    """
    Parses the provided node graph dict and returns it as a NodeGraph object
    :param input_dict: node graph dict
    :return: a NodeGraph object containing the information from the input
    """
    return NodeGraph(version=input_dict["version"], protocol=parse_batadv_graph(input_dict["batadv"]),
                     protocol_type=Protocol.BATMAN_ADV)


def parse_graph_node(input_dict: dict) -> Node:
    """
    Parses the provided node dict and returns it as a Node object
    :param input_dict: node dict
    :return: a Node object containing the information from the input
    """
    return Node(id=input_dict["id"], node_id=input_dict["node_id"])


def parse_batadv_graph(input_dict: dict) -> ProtocolBatmanAdv:
    """
    Parses the provided batman-adv protocol dict and returns it as a ProtocolBatmanAdv object
    :param input_dict: batman-adv protocol dict
    :return: a ProtocolBatmanAdv object containing the information from the input
    """
    nodes = list(map(lambda x: parse_graph_node(x), input_dict["nodes"]))
    return ProtocolBatmanAdv(directed=input_dict["directed"], graph=input_dict["graph"], nodes=nodes,
                             links=list(map(lambda x: parse_graph_link(x, nodes), input_dict["links"])))


def parse_graph_link(input_dict: dict, nodes: list) -> Link:
    """
    Parses the provided graph link dict and returns it as a ProtocolBatmanAdv object
    :param input_dict: batman-adv protocol dict
    :param nodes: list of all graph nodes correctly ordered
    :return: a Link object containing the information from the input
    """
    return Link(source=nodes[input_dict["source"]], target=nodes[input_dict["target"]], vpn=input_dict["vpn"],
                tq=input_dict["tq"], bidirect=input_dict["bidirect"])
