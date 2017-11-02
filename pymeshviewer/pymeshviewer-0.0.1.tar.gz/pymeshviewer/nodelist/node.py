import ipaddress
from datetime import datetime
from typing import List, Dict

from pymeshviewer import Protocol


class MeshVPNPeer:
    def __init__(self, established: bool, established_time: float = None):
        """
        Constructor for a MeshVPNPeer object
        :param established: true if connection to peer is established, false if not
        :param established_time: if connection is established, connection time as a float
        """
        self.established = established
        self.established_time = established_time


class MeshVPNPeerGroup:
    def __init__(self, peers: Dict[str, MeshVPNPeer] = None):
        """
        Constructor for a MeshVPNPeerGroup object
        :param peers: dict of peers
        """
        if peers is None:
            peers = {}
        self.peers = peers


class MeshVPN:
    def __init__(self, groups: Dict[str, MeshVPNPeerGroup] = None):
        """
        Constructor for a MeshVPN object
        :param groups: dict of groups
        """
        if groups is None:
            groups = {}
        self.groups = groups


class Traffic:
    def __init__(self, bytes: int, packets: int, dropped: int):
        """
        Constructor for a Traffic object
        :param bytes: number of transferred bytes
        :param packets: number of transferred packets
        :param dropped: number of dropped packets
        """
        self.bytes = bytes
        self.packets = packets
        self.dropped = dropped


class Processes:
    def __init__(self, total: int, running: int):
        """
        Constructor for a Processes object
        :param total: number of total processes
        :param running: number of running processes
        """
        self.total = total
        self.running = running


class Statistics:
    def __init__(self, node_id: str, clients: int, rootfs_usage: float, loadavg: float, memory_usage: float,
                 uptime: int, idletime: int, gateway: str, processes: Processes, mesh_vpn: MeshVPN,
                 tx: Traffic, rx: Traffic, forward: Traffic, mgmt_tx: Traffic, mgmt_rx: Traffic):
        """
        Constructor for a Statistics object
        :param node_id: node_id of node
        :param clients: total number of clients
        :param rootfs_usage: rootfs usage (0.0 - 1.0)
        :param loadavg: average load
        :param memory_usage: memory usage (0.0 - 1.0)
        :param uptime: uptime of node
        :param idletime: node idle time
        :param gateway: selected gateway
        :param processes: processes on node
        :param mesh_vpn: mesh vpn peers
        :param tx: traffic tx
        :param rx: traffic rx
        :param forward: traffic fowarded
        :param mgmt_tx: traffic mgmt_tx
        :param mgmt_rx: traffic mgmt_rx
        """
        self.node_id = node_id
        self.clients = clients
        self.rootfs_usage = rootfs_usage
        self.loadavg = loadavg
        self.memory_usage = memory_usage
        self.uptime = uptime
        self.idletime = idletime
        self.gateway = gateway
        self.processes = processes
        self.mesh_vpn = mesh_vpn
        self.tx = tx
        self.rx = rx
        self.forward = forward
        self.mgmt_tx = mgmt_tx
        self.mgmt_rx = mgmt_rx


class System:
    def __init__(self, site_code: str):
        """
        Constructor for a System object
        :param site_code: system's site code
        """
        self.site_code = site_code


class Hardware:
    def __init__(self, nproc=0, model=None):
        """
        Constructor for Hardware object
        :param nproc: node nproc
        :param model: node model
        """
        self.nproc = nproc
        self.model = model


class Autoupdater:
    def __init__(self, enabled: bool, branch: str):
        """
        Constructor for Autoupdater object
        :param enabled: autoupdater status
        :param branch: selected branch
        """
        self.enabled = enabled
        self.branch = branch


class BatmanAdv:
    def __init__(self, version: str, compat: int):
        """
        Constructor for BatmanAdv object
        :param version: version of Batman-Adv
        :param compat: compat level
        """
        self.version = version
        self.compat = compat


class Fastd:
    def __init__(self, enabled: bool = False, version: str = None):
        """
        Constructor for Fastd object
        :param enabled: fastd status
        :param version: fastd version
        """
        self.enabled = enabled
        self.version = version


class Firmware:
    def __init__(self, base: str = None, release: str = None):
        """
        Constructor for Firmware object
        :param base: base gluon version
        :param release: custom version scheme
        """
        self.base = base
        self.release = release


class StatusPage:
    def __init__(self, api: int):
        """
        Constructor for StatusPage object
        :param api: api level
        """
        self.api = api


class Software:
    def __init__(self, autoupdater: Autoupdater = None, batman_adv: BatmanAdv = None, fastd: Fastd = None,
                 firmware: Firmware = None, status_page: StatusPage = None):
        """
        Constructor for Software object
        :param autoupdater: autoupdater software information
        :param batman_adv: batman-adv software information
        :param fastd: fastd software information
        :param firmware: firmware software information
        :param status_page: status page software information
        """
        self.autoupdater = autoupdater
        self.batman_adv = batman_adv
        self.fastd = fastd
        self.firmware = firmware
        self.status_page = status_page


class Mesh:
    def __init__(self, wireless: List[str] = None, tunnel: List[str] = None, other: List[str] = None):
        """
        Constructor for Mesh object
        :param wireless: list of wireless mesh interfaces
        :param tunnel: list of tunnel mesh interfaces
        :param other: list of other mesh interfaces
        """
        if other is None:
            other = []
        if tunnel is None:
            tunnel = []
        if wireless is None:
            wireless = []
        self.wireless = wireless
        self.tunnel = tunnel
        self.other = other


class Network:
    def __init__(self, mac: str, addresses: List[ipaddress._IPAddressBase], mesh: Dict[str, Mesh]):
        """
        Constructor for Network object
        :param mac: primary mac address of node
        :param addresses: list of nodes ip addresses
        :param mesh: mesh interfaces of node
        """
        if mesh is None:
            mesh = {}
        if addresses is None:
            addresses = []
        self.mac = mac
        self.addresses = addresses
        self.mesh = mesh

    @property
    def v6_addresses(self) -> List[ipaddress.IPv6Address]:
        """
        Nodes IPv6 addresses
        :return: ipv6 addresses of node
        """
        out = []
        for address in self.addresses:
            if address.version == 6:
                out.append(address)
        return out

    @property
    def v6_global(self) -> List[ipaddress.IPv6Address]:
        """
        Nodes globally routed IPv6 addresses
        :return: globally routed IPv6 addresses of node
        """
        out = []
        for address in self.v6_addresses:
            if address.is_global:
                out.append(address)
        return out

    @property
    def v6_ula(self) -> List[ipaddress.IPv6Address]:
        """
        Nodes ula IPv6 addresses
        :return: ULA IPv6 addresses of node
        """
        out = []
        for address in self.v6_addresses:
            if address.is_private and address not in self.v6_link_local:
                out.append(address)
        return out

    @property
    def v6_link_local(self) -> List[ipaddress.IPv6Address]:
        """
        Nodes Link-Local IPv6 addresses
        :return: Link-Local IPv6 addresses of node
        """
        out = []
        for address in self.v6_addresses:
            if address.is_link_local:
                out.append(address)
        return out


class Location:
    def __init__(self, latitude: float = 0, longitude: float = 0, altitude: float = 0):
        """
        Constructor for Location object
        :param latitude: nodes latitude
        :param longitude: nodes longitude
        :param altitude: nodes altitude
        """
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude


class Nodeinfo:
    def __init__(self, node_id: str, network: Network, system: System, hostname: str, software: Software,
                 hardware: Hardware,
                 vpn: bool, location: Location = None):
        """
        Constructor for Nodeinfo object
        :param node_id: nodes node_id
        :param network: Network object of node
        :param system: System object of node
        :param hostname: nodes hostname
        :param software: Software object of node
        :param hardware: hardware object of node
        :param vpn: boolean indicating vpn server
        :param location: Location object of node
        """
        self.node_id = node_id
        self.network = network
        self.system = system
        self.hostname = hostname
        self.location = location
        self.software = software
        self.hardware = hardware
        self.vpn = vpn


class Neighbour:
    def __init__(self, protocol: Protocol, node_id: str, vpn: bool = False, tq: int = 0, bidirect: bool = False):
        """
        Constructor of Neighbour object
        :param protocol: mesh protocol
        :param node_id: neighbours node_id
        :param vpn: indicating connection is established via vpn
        :param tq: transmission quality (1.0-2.0)
        :param bidirect: bool indicating a bidirectional link
        """
        self.protocol = protocol
        self.node_id = node_id
        self.vpn = vpn
        self.tq = tq
        self.bidirect = bidirect


class Node:
    def __init__(self, firstseen: datetime, lastseen: datetime, online: bool, gateway: bool, statistics: Statistics,
                 nodeinfo: Nodeinfo, neighbours: List[str] = None):
        """
        Constructor for Node object
        :param firstseen: datetime of nodes first sight
        :param lastseen: datetime of nodes last sight
        :param online: bool indicating online status of node
        :param gateway: bool indicating if node is a gateway
        :param statistics: Statistics object of node
        :param nodeinfo: Nodeinfo object of node
        :param neighbours: nodes neighbours
        """
        if neighbours is None:
            neighbours = []
        self.firstseen = firstseen
        self.lastseen = lastseen
        self.online = online
        self.gateway = gateway
        self.statistics = statistics
        self.nodeinfo = nodeinfo
        self.neighbours = neighbours

    @property
    def vpn_enabled(self):
        """
        Return VPN enabled status
        :return: vpn enabled status
        """
        if self.nodeinfo.software.fastd.enabled is True:
            return True
        return False

    @property
    def vpn_active(self):
        """
        Return VPN established status
        :return: vpn established status
        """
        if self.statistics.mesh_vpn is None:
            return False
        for k, v in self.statistics.mesh_vpn.groups.items():
            for k, v in v.peers.items():
                if v and v.established is True:
                    return True
        return False
