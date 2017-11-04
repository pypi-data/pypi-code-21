import ipaddress
import unittest
from datetime import datetime

from pymeshviewer.node import Node, Nodeinfo, System, Hardware, Software, StatusPage, Firmware, MeshVPNPeer, \
    MeshVPNPeerGroup, MeshVPN, Traffic, Processes, Statistics, Mesh, Network, Location, Autoupdater, BatmanAdv, Fastd


class NodeTest(unittest.TestCase):
    def setUp(self):
        """
        Initialize Tests
        """

        # Peer
        self.peer_1_established = False
        self.peer_1 = MeshVPNPeer(established=self.peer_1_established)
        self.peer_2_established = True
        self.peer_2_established_time = 300.33
        self.peer_2 = MeshVPNPeer(established=self.peer_2_established, established_time=self.peer_2_established_time)

        # Peer Group
        self.peers_dict = {"peer1": self.peer_1, "peer2": self.peer_2}
        self.peer_group = MeshVPNPeerGroup(self.peers_dict)

        # Mesh VPN
        self.mesh_vpn_groups = {"backbone": self.peer_group}
        self.mesh_vpn = MeshVPN(self.mesh_vpn_groups)

        # Traffic
        self.tx_bytes = 500
        self.tx_dropped = 10
        self.tx_packets = 50
        self.tx = Traffic(bytes=self.tx_bytes, dropped=self.tx_dropped, packets=self.tx_packets)

        self.rx_bytes = 553
        self.rx_dropped = 99
        self.rx_packets = 399
        self.rx = Traffic(bytes=self.rx_bytes, dropped=self.rx_dropped, packets=self.rx_packets)

        self.forward_bytes = 53040
        self.forward_dropped = 944
        self.forward_packets = 3244
        self.forward = Traffic(bytes=self.forward_bytes, dropped=self.forward_dropped, packets=self.forward_packets)

        self.mgmt_tx_bytes = 324234
        self.mgmt_tx_dropped = 232
        self.mgmt_tx_packets = 2354
        self.mgmt_tx = Traffic(bytes=self.mgmt_tx_bytes, dropped=self.mgmt_tx_dropped, packets=self.mgmt_tx_packets)

        self.mgmt_rx_bytes = 5241
        self.mgmt_rx_dropped = 34
        self.mgmt_rx_packets = 647
        self.mgmt_rx = Traffic(bytes=self.mgmt_rx_bytes, dropped=self.mgmt_rx_dropped, packets=self.mgmt_rx_packets)

        # Processes
        self.processes_total = 500
        self.processes_running = 100
        self.processes = Processes(total=self.processes_total, running=self.processes_running)

        # Statistics
        self.node_id = "deadbeefffda"
        self.client_count = 5
        self.rootfs_usage = 0.4124
        self.load = 0.45243242
        self.memory_usage = 0.55
        self.uptime = 133842
        self.idletime = 400
        self.gateway = "de:ad:be:ef:ff:ff"
        self.statistics = Statistics(node_id=self.node_id, clients=self.client_count, rootfs_usage=self.rootfs_usage,
                                     loadavg=self.load, memory_usage=self.memory_usage, uptime=self.uptime,
                                     idletime=self.idletime, gateway=self.gateway, processes=self.processes,
                                     mesh_vpn=self.mesh_vpn, tx=self.tx, rx=self.rx,
                                     forward=self.forward, mgmt_tx=self.mgmt_tx, mgmt_rx=self.mgmt_rx)
        # Mesh
        self.mesh_ifs_wireless = ["de:ad:be:ef:f0:da", "de:ad:be:ef:f1:da"]
        self.mesh_ifs_tunnel = ["de:ad:be:ef:f1:df"]
        self.mesh_ifs_other = ["de:ad:be:ef:f1:de"]
        self.mesh_ifs = Mesh(wireless=self.mesh_ifs_wireless, tunnel=self.mesh_ifs_tunnel, other=self.mesh_ifs_other)

        # Network
        self.mac = "de:ad:be:ef:ff:da"
        self.v6_address_global = ipaddress.ip_address("2001:67C:2ED8:6100:DCAD:BEFF:FEEF:FFDA".lower())
        self.v6_address_ula = ipaddress.ip_address("fd01:67C:2ED8:6100:DCAD:BEFF:FEEF:FFDA".lower())
        self.v6_address_link_local = ipaddress.ip_address("fe80::DCAD:BEFF:FEEF:FFDA".lower())
        self.addresses = [
            self.v6_address_global,
            self.v6_address_ula,
            self.v6_address_link_local
        ]
        self.mesh = {"bat0": self.mesh_ifs}
        self.network = Network(mac=self.mac, addresses=self.addresses, mesh=self.mesh)

        # System
        self.site_code = "ffda"
        self.system = System(self.site_code)

        # Location
        self.latitude = 49.849
        self.longitude = 8.733
        self.altitude = 19.4
        self.location = Location(latitude=self.latitude, longitude=self.longitude, altitude=self.altitude)

        # Autoupdater
        self.autoupdater_enabled = True
        self.autoupdater_branch = "stable"
        self.autoupdater = Autoupdater(enabled=self.autoupdater_enabled, branch=self.autoupdater_branch)

        # Batman-Adv
        self.batman_adv_version = "2017.2"
        self.batman_adv_compat = 15
        self.batman_adv = BatmanAdv(version=self.batman_adv_version, compat=self.batman_adv_compat)

        # Fastd
        self.fastd_version = "v18"
        self.fastd = Fastd(version=self.fastd_version)

        # Firmware
        self.firmware_base = "gluon-v2017.1.3"
        self.firmware_release = "1.0.3"
        self.firmware = Firmware(base=self.firmware_base, release=self.firmware_release)

        # StatusPage
        self.status_page_api = 1
        self.status_page = StatusPage(api=self.status_page_api)

        # Software
        self.software = Software(autoupdater=self.autoupdater, batman_adv=self.batman_adv, fastd=self.fastd,
                                 firmware=self.firmware, status_page=self.status_page)
        # Hardware
        self.hardware_nproc = 1
        self.hardware_model = "TP-Link TL-WR1043N/ND v4"
        self.hardware = Hardware(nproc=self.hardware_nproc, model=self.hardware_model)

        # Nodeinfo
        self.hostname = "64283-test"
        self.vpn = False
        self.nodeinfo = Nodeinfo(node_id=self.node_id, network=self.network, system=self.system, hostname=self.hostname,
                                 location=self.location, software=self.software, hardware=self.hardware, vpn=self.vpn)

        # Node
        self.now = datetime.now()
        self.online = True
        self.gateway_bool = False
        self.node = Node(firstseen=self.now, lastseen=self.now, online=self.online, gateway=self.gateway_bool,
                         statistics=self.statistics,
                         nodeinfo=self.nodeinfo)

    def test_traffic(self):
        self.assertEqual(self.tx.bytes, self.tx_bytes)
        self.assertEqual(self.tx.packets, self.tx_packets)
        self.assertEqual(self.tx.dropped, self.tx_dropped)

        self.assertEqual(self.rx.bytes, self.rx_bytes)
        self.assertEqual(self.rx.packets, self.rx_packets)
        self.assertEqual(self.rx.dropped, self.rx_dropped)

        self.assertEqual(self.forward.bytes, self.forward_bytes)
        self.assertEqual(self.forward.packets, self.forward_packets)
        self.assertEqual(self.forward.dropped, self.forward_dropped)

        self.assertEqual(self.mgmt_tx.bytes, self.mgmt_tx_bytes)
        self.assertEqual(self.mgmt_tx.packets, self.mgmt_tx_packets)
        self.assertEqual(self.mgmt_tx.dropped, self.mgmt_tx_dropped)

        self.assertEqual(self.mgmt_rx.bytes, self.mgmt_rx_bytes)
        self.assertEqual(self.mgmt_rx.packets, self.mgmt_rx_packets)
        self.assertEqual(self.mgmt_rx.dropped, self.mgmt_rx_dropped)

    def test_processes(self):
        self.assertEqual(self.processes.total, self.processes_total)
        self.assertEqual(self.processes.running, self.processes_running)

    def test_statistics(self):
        self.assertEqual(self.statistics.node_id, self.node_id)
        self.assertEqual(self.statistics.clients, self.client_count)
        self.assertEqual(self.statistics.rootfs_usage, self.rootfs_usage)
        self.assertEqual(self.statistics.loadavg, self.load)
        self.assertEqual(self.statistics.memory_usage, self.memory_usage)
        self.assertEqual(self.statistics.uptime, self.uptime)
        self.assertEqual(self.statistics.idletime, self.idletime)
        self.assertEqual(self.statistics.gateway, self.gateway)
        self.assertEqual(self.statistics.processes, self.processes)

        self.assertEqual(self.statistics.mesh_vpn, self.mesh_vpn)

        self.assertEqual(self.statistics.tx, self.tx)
        self.assertEqual(self.statistics.rx, self.rx)
        self.assertEqual(self.statistics.forward, self.forward)
        self.assertEqual(self.statistics.mgmt_rx, self.mgmt_rx)
        self.assertEqual(self.statistics.mgmt_tx, self.mgmt_tx)

    def test_mesh_ifs(self):
        self.assertEqual(self.mesh_ifs.tunnel, self.mesh_ifs_tunnel)
        self.assertEqual(self.mesh_ifs.wireless, self.mesh_ifs_wireless)
        self.assertEqual(self.mesh_ifs.other, self.mesh_ifs_other)

    def test_network(self):
        self.assertEqual(self.network.mac, self.mac)
        self.assertEqual(self.network.addresses, self.addresses)
        self.assertEqual(self.network.mesh, self.mesh)
        self.assertEqual(self.network.v6_addresses, self.addresses)
        self.assertEqual(self.network.v6_global, [self.v6_address_global])
        self.assertEqual(self.network.v6_ula, [self.v6_address_ula])
        self.assertEqual(self.network.v6_link_local, [self.v6_address_link_local])

    def test_system(self):
        self.assertEqual(self.system.site_code, self.site_code)

    def test_location(self):
        self.assertEqual(self.location.latitude, self.latitude)
        self.assertEqual(self.location.longitude, self.longitude)
        self.assertEqual(self.location.altitude, self.altitude)

    def test_software_autoupdater(self):
        self.assertEqual(self.autoupdater.enabled, self.autoupdater_enabled)
        self.assertEqual(self.autoupdater.branch, self.autoupdater_branch)

    def test_software_batman_adv(self):
        self.assertEqual(self.batman_adv.version, self.batman_adv_version)
        self.assertEqual(self.batman_adv.compat, self.batman_adv_compat)

    def test_software_fastd(self):
        self.assertEqual(self.fastd.version, self.fastd_version)

    def test_software_firmware(self):
        self.assertEqual(self.firmware.base, self.firmware_base)
        self.assertEqual(self.firmware.release, self.firmware_release)

    def test_software_status_page(self):
        self.assertEqual(self.status_page.api, self.status_page_api)

    def test_software(self):
        self.assertEqual(self.software.autoupdater, self.autoupdater)
        self.assertEqual(self.software.batman_adv, self.batman_adv)
        self.assertEqual(self.software.fastd, self.fastd)
        self.assertEqual(self.software.firmware, self.firmware)
        self.assertEqual(self.software.status_page, self.status_page)

    def test_hardware(self):
        self.assertEqual(self.hardware.nproc, self.hardware_nproc)
        self.assertEqual(self.hardware.model, self.hardware_model)

    def test_mesh_vpn_peer(self):
        self.assertEqual(self.peer_1.established, self.peer_1_established)
        self.assertEqual(self.peer_1.established_time, None)
        self.assertEqual(self.peer_2.established, self.peer_2_established)
        self.assertEqual(self.peer_2.established_time, self.peer_2_established_time)

    def test_mesh_vpn_group(self):
        self.assertEqual(self.peer_group.peers, self.peers_dict)

    def test_mesh_vpn(self):
        self.assertEqual(self.mesh_vpn.groups, self.mesh_vpn_groups)

    def test_nodeinfo(self):
        self.assertEqual(self.nodeinfo.node_id, self.node_id)
        self.assertEqual(self.nodeinfo.network, self.network)
        self.assertEqual(self.nodeinfo.system, self.system)
        self.assertEqual(self.nodeinfo.hostname, self.hostname)
        self.assertEqual(self.nodeinfo.location, self.location)
        self.assertEqual(self.nodeinfo.software, self.software)
        self.assertEqual(self.nodeinfo.hardware, self.hardware)
        self.assertEqual(self.nodeinfo.vpn, self.vpn)

    def test_node(self):
        self.assertEqual(self.node.firstseen, self.now)
        self.assertEqual(self.node.lastseen, self.now)
        self.assertEqual(self.node.online, self.online)
        self.assertEqual(self.node.gateway, self.gateway_bool)
        self.assertEqual(self.node.statistics, self.statistics)
        self.assertEqual(self.node.nodeinfo, self.nodeinfo)
