import json

from pymeshviewer.node import *
from pymeshviewer.nodesjson import NodesJSON
from pymeshviewer.parser import parse_datetime


def parse_node(node_dict: dict) -> Node:
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
    return NodesJSON(list(map(lambda x: parse_node(x), root_obj["nodes"])), root_obj["version"], parse_datetime(
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
                        gateway=statistics_dict.get("gateway", None), processes=parse_processes(statistics_dict["processes"]),
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


def parse_network(network_dict: dict) -> Network:
    """
    Parses the provided network dict in ffrgb-meshviewer format
    :param network_dict: network section dict
    :return: a Network object containing the information from the input
    """
    output = Network(mac=network_dict["mac"],
                     addresses=list(map(lambda x: ipaddress.ip_address(x), network_dict["addresses"])),
                     mesh=parse_mesh_interfaces(network_dict["mesh"]))
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
            output.autoupdater = Autoupdater(enabled=v.get("enabled", False), branch=v.get("branch", None))
        elif k == "batman-adv":
            output.batman_adv = BatmanAdv(version=v.get("version", None), compat=v.get("compat", None))
        elif k == "fastd":
            output.fastd = Fastd(enabled=v.get("enabled", False), version=v.get("version", None))
        elif k == "firmware":
            output.firmware = Firmware(base=v.get("base", None), release=v.get("release", None))
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
