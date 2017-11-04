import ipaddress
import os
import unittest

from pymeshviewer.parser import parse_datetime, parse_nodes_json


class NodelistParserTest(unittest.TestCase):
    def setUp(self):
        """
        Initialize Tests
        """

        file = open(os.path.dirname(os.path.realpath(__file__)) + os.sep + "testfiles/yanic_example_town_nodes.json",
                    "r")
        self.file_content = file.read()
        self.nodelist = parse_nodes_json(self.file_content)
        file.close()

    def test_size(self):
        """
        Verify the number of parsed nodes is correct
        """
        self.assertEqual(self.nodelist.node_count, 4)

    def test_firstseen(self):
        self.assertEqual(self.nodelist.nodes[0].firstseen, parse_datetime("2016-11-27T03:52:55+0000"))

    def test_lastseen(self):
        self.assertEqual(self.nodelist.nodes[0].lastseen, parse_datetime("2017-10-21T00:33:50+0200"))

    def test_flags(self):
        self.assertTrue(self.nodelist.nodes[0].online)
        self.assertTrue(self.nodelist.nodes[0].gateway)

    def test_statistics(self):
        self.assertEqual(self.nodelist.nodes[0].statistics.node_id, "daff61000302")
        self.assertEqual(self.nodelist.nodes[0].statistics.clients, 0)
        self.assertEqual(self.nodelist.nodes[0].statistics.loadavg, 1.11)
        self.assertEqual(self.nodelist.nodes[0].statistics.memory_usage, 0.34640929437841284)
        self.assertEqual(self.nodelist.nodes[0].statistics.uptime, 1463731.06)
        self.assertEqual(self.nodelist.nodes[0].statistics.idletime, 2674140.98)
        self.assertEqual(self.nodelist.nodes[0].statistics.processes.total, 124)
        self.assertEqual(self.nodelist.nodes[0].statistics.processes.running, 4)

        self.assertEqual(self.nodelist.nodes[0].statistics.tx.bytes, 7400661063510)
        self.assertEqual(self.nodelist.nodes[0].statistics.tx.packets, 6481364061)
        self.assertEqual(self.nodelist.nodes[0].statistics.tx.dropped, 8402057)

        self.assertEqual(self.nodelist.nodes[0].statistics.rx.bytes, 811005896638)
        self.assertEqual(self.nodelist.nodes[0].statistics.rx.packets, 4766761900)

        self.assertEqual(self.nodelist.nodes[0].statistics.forward.bytes, 4729587096438)
        self.assertEqual(self.nodelist.nodes[0].statistics.forward.packets, 9701545372)

        self.assertEqual(self.nodelist.nodes[0].statistics.mgmt_tx.bytes, 51533836800)
        self.assertEqual(self.nodelist.nodes[0].statistics.mgmt_tx.packets, 145173118)

        self.assertEqual(self.nodelist.nodes[0].statistics.mgmt_rx.bytes, 1429253469038)
        self.assertEqual(self.nodelist.nodes[0].statistics.mgmt_rx.packets, 3289390848)

    def test_nodeinfo(self):
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.node_id, "daff61000302")

        self.assertEqual(self.nodelist.nodes[0].nodeinfo.network.mac, "da:ff:61:00:03:02")
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.network.addresses, [
            ipaddress.ip_address("fe80::543a:9dff:fe11:4238"),
            ipaddress.ip_address("2001:67c:2ed8:6100::3"),
            ipaddress.ip_address("fd01:67c:2ed8:6100::3"),
            ipaddress.ip_address("fe80::d8ff:61ff:fe00:304")
        ])
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.network.mesh["ffda-bat"].tunnel, [
            "da:ff:61:00:03:05",
            "da:ff:61:00:03:03",
            "da:ff:61:01:03:03"
        ])
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.hostname, "gw03.darmstadt.freifunk.net")
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.software.autoupdater.enabled, False)
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.software.autoupdater.branch, None)
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.software.batman_adv.version, "2017.3")
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.software.batman_adv.compat, None)
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.software.fastd.enabled, True)
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.software.fastd.version, "v18")
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.software.firmware.base, "Debian")
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.software.firmware.release, "8.9")
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.software.status_page.api, 0)
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.hardware.nproc, 3)
        self.assertEqual(self.nodelist.nodes[0].nodeinfo.vpn, True)
