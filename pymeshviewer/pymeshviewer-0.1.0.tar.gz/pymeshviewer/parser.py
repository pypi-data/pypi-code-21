import ipaddress
import json
from datetime import datetime
from typing import Dict

from pymeshviewer import Protocol
from pymeshviewer.graph import Node as GraphNode, LinkType
from pymeshviewer.graph import NodeGraph, ProtocolBatmanAdv, Link
from pymeshviewer.meshviewerjson import MeshviewerJSON
from pymeshviewer.node import Network, Location, Autoupdater, Firmware, Statistics, Nodeinfo, System, Software, \
    Hardware, Node, Traffic, Processes, Mesh, BatmanAdv, Fastd, StatusPage, MeshVPNPeer, MeshVPNPeerGroup, MeshVPN, \
    Neighbour
from pymeshviewer.nodesjson import NodesJSON


def parse_datetime(datetime_string: str) -> datetime:
    """
    Parses the datetime string from meshviewer json and returns it as a datetime object
    :param datetime_string: datetime string from yanic json
    :return: parsed datetime string as datetime object
    """
    return datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M:%S%z')


def parse_network(network_dict: dict) -> Network:
    """
    Parses the provided network dict in ffrgb-meshviewer format
    :param network_dict: network section dict
    :return: a Network object containing the information from the input
    """
    mesh = None
    if "mesh" in network_dict:
        mesh = parse_mesh_interfaces(network_dict["mesh"])
    output = Network(mac=network_dict["mac"],
                     addresses=list(map(lambda x: ipaddress.ip_address(x), network_dict["addresses"])),
                     mesh=mesh)
    return output


def parse_location(location_dict: dict) -> Location:
    """
    Parses the provided location dict in ffrgb-meshviewer format
    :param location_dict: location section dict
    :return: a Location object containing the information from the input
    """
    output = Location()
    output.latitude = location_dict["latitude"]
    output.longitude = location_dict["longitude"]
    return output


def parse_autoupdater(autoupdater_dict: dict):
    return Autoupdater(enabled=autoupdater_dict.get("enabled", False), branch=autoupdater_dict.get("branch", None))


def parse_firmware(firmware_dict: Dict[str, str]):
    return Firmware(base=firmware_dict.get("base", None), release=firmware_dict.get("release", None))


def parse_graph_json(input_string: str) -> NodeGraph:
    """
    Parses the provided node graph json string and returns it as a NodeGraph object
    :param input_string: node graph json string
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
    return GraphNode(id=input_dict["id"], node_id=input_dict["node_id"])


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


def parse_nodesjson_node(node_dict: dict) -> Node:
    """
    Parses the provided node-dict in ffrgb-meshviewer format
    :param node_dict: dict containing a single object of node type
    :return: a Node object containing the information from the input
    """
    output = Node(
        firstseen=parse_datetime(node_dict['firstseen']),
        lastseen=parse_datetime(node_dict['lastseen']),
        online=node_dict["flags"]["online"],
        gateway=node_dict["flags"]["gateway"],
        statistics=parse_statistics(node_dict["statistics"]),
        nodeinfo=parse_nodeinfo(node_dict["nodeinfo"]))
    return output


def parse_nodes_json(nodes_str: str) -> NodesJSON:
    """
    Parses the provided nodelist json in ffrgb-meshviewer format
    :param nodes_str: nodelist json
    :return: a Nodelist object containing the information from the input
    """
    root_obj = json.loads(nodes_str)
    return NodesJSON(list(map(lambda x: parse_nodesjson_node(x), root_obj["nodes"])), root_obj["version"],
                     parse_datetime(
                         root_obj["timestamp"]))


def parse_traffic(traffic_dict: dict) -> Traffic:
    """
    Parses the provided traffic dict in ffrgb-meshviewer format
    :param traffic_dict: traffic section dict
    :return: a Traffic object containing the information from the input
    """
    return Traffic(bytes=traffic_dict.get("bytes", None),
                   packets=traffic_dict.get("packets", None),
                   dropped=traffic_dict.get("dropped", None))


def parse_processes(processes_dict: dict) -> Processes:
    """
    Parses the provided processes dict in ffrgb-meshviewer format
    :param processes_dict: processes section dict
    :return: a Processes object containing the information from the input
    """
    return Processes(total=processes_dict["total"], running=processes_dict["running"])


def parse_statistics(statistics_dict: dict) -> Statistics:
    """
    Parses the provided statistics dict in ffrgb-meshviewer format
    :param statistics_dict: statistics section dict
    :return: a Statistics object containing the information from the input
    """
    mesh_vpn = None
    if "mesh_vpn" in statistics_dict:
        mesh_vpn = parse_mesh_vpn(statistics_dict["mesh_vpn"])

    output = Statistics(node_id=statistics_dict["node_id"], clients=statistics_dict["clients"],
                        rootfs_usage=statistics_dict.get("rootfs_usage", None),
                        loadavg=statistics_dict.get("loadavg", None), memory_usage=statistics_dict["memory_usage"],
                        uptime=statistics_dict["uptime"], idletime=statistics_dict["idletime"],
                        gateway=statistics_dict.get("gateway", None),
                        processes=parse_processes(statistics_dict["processes"]),
                        mesh_vpn=mesh_vpn,
                        tx=parse_traffic(statistics_dict["traffic"]["tx"]),
                        rx=parse_traffic(statistics_dict["traffic"]["rx"]),
                        forward=parse_traffic(statistics_dict["traffic"]["forward"]),
                        mgmt_tx=parse_traffic(statistics_dict["traffic"]["mgmt_tx"]),
                        mgmt_rx=parse_traffic(statistics_dict["traffic"]["mgmt_rx"]))
    return output


def parse_mesh_interfaces(mesh_interfaces_dict: dict) -> dict:
    """
    Parses the provided mesh-interfaces dict in ffrgb-meshviewer format
    :param mesh_interfaces_dict: mesh-interfaces section dict
    :return: a dict containing the information from the input as Mesh type
    """
    output = {}
    for k, v in mesh_interfaces_dict.items():
        v = v["interfaces"]
        wireless = []
        tunnel = []
        other = []
        if 'wireless' in v:
            wireless = v["wireless"]
        if 'tunnel' in v:
            tunnel = v["tunnel"]
        if 'other' in v:
            other = v["other"]
        output[k] = Mesh(wireless=wireless, tunnel=tunnel, other=other)
    return output


def parse_system(system_dict: dict) -> System:
    """
    Parses the provided system dict in ffrgb-meshviewer format
    :param system_dict: system section dict
    :return: a System object containing the information from the input
    """
    return System(system_dict.get("site_code", None))


def parse_software(software_dict: dict) -> Software:
    """
    Parses the provided software dict in ffrgb-meshviewer format
    :param software_dict: software section dict
    :return: a Software object containing the information from the input
    """
    output = Software()
    for k, v in software_dict.items():
        if k == "autoupdater":
            output.autoupdater = parse_autoupdater(v)
        elif k == "batman-adv":
            output.batman_adv = BatmanAdv(version=v.get("version", None), compat=v.get("compat", None))
        elif k == "fastd":
            output.fastd = Fastd(enabled=v.get("enabled", False), version=v.get("version", None))
        elif k == "firmware":
            output.firmware = parse_firmware(v)
        elif k == "status-page":
            output.status_page = StatusPage(v.get("api", None))
    return output


def parse_hardware(hardware_dict: dict) -> Hardware:
    """
    Parses the provided hardware dict in ffrgb-meshviewer format
    :param hardware_dict: hardware section dict
    :return: a Hardware object containing the information from the input
    """
    return Hardware(nproc=hardware_dict.get("nproc", None), model=hardware_dict.get("model", None))


def parse_mesh_vpn_peer(peer_dict: dict) -> MeshVPNPeer:
    """
    Parses the provided peer section dict in ffrgb-meshviewer format
    :param peer_dict: peer section dict
    :return: a MeshVPNPeer object containing the information from the input
    """
    if peer_dict is None:
        return MeshVPNPeer(established=False)
    return MeshVPNPeer(established=True, established_time=peer_dict["established"])


def parse_mesh_vpn_group(group_dict: dict) -> MeshVPNPeerGroup:
    """
    Parses the provided mesh-vpn group section dict in ffrgb-meshviewer format
    :param group_dict: group section dict
    :return: a MeshVPNPeerGroup object containing the information from the input
    """
    peers = {}
    for k, v in group_dict["peers"].items():
        peers[k] = parse_mesh_vpn_peer(v)
    return MeshVPNPeerGroup(peers)


def parse_mesh_vpn(mesh_vpn_dict: dict) -> MeshVPN:
    """
    Parses the provided mesh-vpn section dict in ffrgb-meshviewer format
    :param mesh_vpn_dict: mesh-vpn section dict
    :return: a MeshVPN object containing the information from the input
    """
    groups = {}
    for k, v in mesh_vpn_dict["groups"].items():
        groups[k] = parse_mesh_vpn_group(v)
    return MeshVPN(groups)


def parse_nodeinfo(nodeinfo_dict: dict) -> Nodeinfo:
    """
    Parses the provided nodeinfo section dict in ffrgb-meshviewer format
    :param nodeinfo_dict: nodeinfo section dict
    :return: a Nodeinfo object containing the information from the input
    """
    output = Nodeinfo(
        node_id=nodeinfo_dict["node_id"],
        network=parse_network(nodeinfo_dict["network"]),
        hostname=nodeinfo_dict["hostname"],
        software=parse_software(nodeinfo_dict["software"]),
        hardware=parse_hardware(nodeinfo_dict["hardware"]),
        system=parse_system(nodeinfo_dict["system"]),
        vpn=nodeinfo_dict["vpn"])
    if "location" in nodeinfo_dict.keys():
        output.location = parse_location(nodeinfo_dict["location"])
    return output


def parse_meshviewer_json(input_str: str) -> MeshviewerJSON:
    root_obj = json.loads(input_str)
    nodes = list(map(lambda x: parse_meshviewer_node(x), root_obj["nodes"]))
    links = list(map(lambda x: parse_meshviewer_link(x), root_obj["links"]))

    meshviewer_json = MeshviewerJSON(nodes=nodes, links=links, timestamp=parse_datetime(root_obj["timestamp"]))
    for link in links:
        src = meshviewer_json.get_node(link.source)
        dst = meshviewer_json.get_node(link.target)

        src.neighbours.append(Neighbour(protocol=Protocol.GENERAL, node_id=link.target, vpn=link.vpn, tq=link.tq))
        dst.neighbours.append(Neighbour(protocol=Protocol.GENERAL, node_id=link.source, vpn=link.vpn, tq=link.tq))

    return meshviewer_json


def parse_meshviewer_link_type(input_str: str) -> LinkType:
    """
    Returns the Meshviewer.json link type as a LinkType
    :param input_str: link type from meshviewer
    :return: LinkType
    """
    if input_str == "wifi":
        return LinkType.WIFI
    if input_str == "vpn":
        return LinkType.VPN
    return LinkType.OTHER


def parse_meshviewer_link(link_dict: dict) -> Link:
    """
    Parses a Meshviewer.json link
    :param link_dict: link
    :return: Parsed link
    """
    return Link(source=link_dict["source"],
                target=link_dict["target"],
                source_tq=link_dict["source_tq"],
                target_tq=link_dict["target_tq"],
                link_type=parse_meshviewer_link_type(link_dict["type"]))


def parse_meshviewer_node(node_dict: dict) -> Node:
    """
    Parses a node from meshviewer.json
    :param node_dict: node
    :return: Parsed node of type node
    """
    autoupdater = None
    if "autoupdater" in node_dict:
        autoupdater = parse_autoupdater(node_dict["autoupdater"])

    firmware = None
    if "firmware" in node_dict:
        firmware = parse_firmware(node_dict["firmware"])

    statistics = Statistics(node_id=node_dict["node_id"],
                            clients=node_dict["clients"],
                            clients_wifi24=node_dict["clients_wifi24"],
                            clients_wifi5=node_dict["clients_wifi5"],
                            clients_other=node_dict["clients_other"],
                            rootfs_usage=node_dict.get("rootfs_usage", 0),
                            loadavg=node_dict["loadavg"],
                            memory_usage=node_dict["memory_usage"],
                            uptime=int((parse_datetime(node_dict["lastseen"]) - parse_datetime(
                                node_dict["uptime"])).total_seconds()),
                            idletime=0,
                            gateway=node_dict.get("gateway", None)
                            )
    location = None
    if "location" in node_dict:
        location = parse_location(node_dict["location"])
    nodeinfo = Nodeinfo(node_id=node_dict["node_id"],
                        network=parse_network(node_dict["network"]),
                        system=System(site_code=node_dict["site_code"]),
                        hostname=node_dict["hostname"],
                        location=location,
                        software=Software(autoupdater=autoupdater,
                                          firmware=firmware),
                        hardware=Hardware(model=node_dict.get("model", None),
                                          nproc=node_dict["nproc"]),
                        vpn=node_dict["vpn"])
    return Node(firstseen=parse_datetime(node_dict["firstseen"], ),
                lastseen=parse_datetime(node_dict["lastseen"]),
                online=node_dict["is_online"],
                gateway=node_dict["is_gateway"],
                statistics=statistics,
                nodeinfo=nodeinfo
                )
