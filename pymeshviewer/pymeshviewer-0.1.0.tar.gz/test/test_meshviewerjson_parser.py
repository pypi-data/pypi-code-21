import os
import unittest

from pymeshviewer.graph import LinkType
from pymeshviewer.parser import parse_meshviewer_json, parse_datetime


class MeshviewerJsonTest(unittest.TestCase):
    def setUp(self):
        nodelist_file = open(
            os.path.dirname(os.path.realpath(__file__)) + os.sep + "testfiles/yanic_example_town_meshviewer.json", "r")
        self.meshviewer_json = parse_meshviewer_json(nodelist_file.read())
        nodelist_file.close()

    def test_meshviewer_json(self):
        """
        Assert correct number of elements
        """
        self.assertEqual(len(self.meshviewer_json.nodes), 4)
        self.assertEqual(len(self.meshviewer_json.links), 3)

    def test_links(self):
        """
        Assert links are correctly parsed
        """
        self.assertEqual(self.meshviewer_json.links[0].link_type, LinkType.WIFI)
        self.assertEqual(self.meshviewer_json.links[0].source, "c04a00dd692a")
        self.assertEqual(self.meshviewer_json.links[0].target, "60e3272f92b2")
        self.assertEqual(self.meshviewer_json.links[0].source_tq, 0.8627451)
        self.assertEqual(self.meshviewer_json.links[0].target_tq, 0.9529412)

        self.assertEqual(self.meshviewer_json.links[1].link_type, LinkType.OTHER)
        self.assertEqual(self.meshviewer_json.links[1].source, "daff61000302")
        self.assertEqual(self.meshviewer_json.links[1].target, "daff61000402")
        self.assertEqual(self.meshviewer_json.links[1].source_tq, 1)
        self.assertEqual(self.meshviewer_json.links[1].target_tq, 1)

        self.assertEqual(self.meshviewer_json.links[2].link_type, LinkType.VPN)
        self.assertEqual(self.meshviewer_json.links[2].source, "daff61000302")
        self.assertEqual(self.meshviewer_json.links[2].target, "c04a00dd692a")
        self.assertEqual(self.meshviewer_json.links[2].source_tq, 1)
        self.assertEqual(self.meshviewer_json.links[2].target_tq, 1)

    def test_nodes(self):
        """
        Assert nodes are parsed correctly
        """
        node_0 = self.meshviewer_json.get_node("daff61000302")
        self.assertEqual(node_0.firstseen, parse_datetime("2016-11-27T03:52:55+0000"))
        self.assertEqual(node_0.lastseen, parse_datetime("2017-10-21T00:33:50+0200"))
        self.assertTrue(node_0.online)
        self.assertTrue(node_0.gateway)

        self.assertEqual(node_0.statistics.clients, 0)
        self.assertEqual(node_0.statistics.loadavg, 1.11)
        self.assertEqual(node_0.statistics.memory_usage, 0.34640929437841284)
        self.assertEqual(node_0.statistics.uptime, 20)
        self.assertEqual(node_0.statistics.node_id, "daff61000302")
        self.assertEqual(node_0.statistics.gateway, None)
        self.assertEqual(node_0.statistics.processes, None)
        self.assertEqual(node_0.statistics.mesh_vpn, None)
        self.assertEqual(node_0.statistics.rx, None)
        self.assertEqual(node_0.statistics.tx, None)
        self.assertEqual(node_0.statistics.forward, None)
        self.assertEqual(node_0.statistics.mgmt_rx, None)
        self.assertEqual(node_0.statistics.mgmt_tx, None)
        self.assertEqual(node_0.statistics.rootfs_usage, 0)

        self.assertEqual(node_0.nodeinfo.node_id, "daff61000302")
        self.assertEqual(node_0.nodeinfo.location, None)
        self.assertEqual(node_0.nodeinfo.hardware.model, None)
        self.assertEqual(node_0.nodeinfo.hardware.nproc, 3)
        self.assertEqual(node_0.nodeinfo.system.site_code, "ffda")
        self.assertEqual(node_0.nodeinfo.hostname, "gw03.darmstadt.freifunk.net")

        self.assertEqual(node_0.nodeinfo.software.autoupdater.enabled, False)
        self.assertEqual(node_0.nodeinfo.software.autoupdater.branch, None)

        self.assertEqual(node_0.nodeinfo.software.firmware.base, "Debian")
        self.assertEqual(node_0.nodeinfo.software.firmware.release, None)

        node_2 = self.meshviewer_json.get_node("c04a00dd692a")
        self.assertEqual(node_2.firstseen, parse_datetime("2015-10-16T11:00:02+0000"))
        self.assertEqual(node_2.lastseen, parse_datetime("2017-11-02T21:08:59+0100"))
        self.assertTrue(node_2.online)
        self.assertFalse(node_2.gateway)

        self.assertEqual(node_2.statistics.clients, 5)
        self.assertEqual(node_2.statistics.clients_wifi24, 1)
        self.assertEqual(node_2.statistics.clients_wifi5, 3)
        self.assertEqual(node_2.statistics.clients_other, 1)
        self.assertEqual(node_2.statistics.clients, 5)
        self.assertEqual(node_2.statistics.loadavg, 0.45)
        self.assertEqual(node_2.statistics.memory_usage, 0.2151159077846606)
        self.assertEqual(node_2.statistics.rootfs_usage, 0.0904)
        self.assertEqual(node_2.statistics.uptime, 93681)
        self.assertEqual(node_2.statistics.node_id, "c04a00dd692a")
        self.assertEqual(node_2.statistics.gateway, "daff61000605")
        self.assertEqual(node_2.statistics.processes, None)
        self.assertEqual(node_2.statistics.mesh_vpn, None)
        self.assertEqual(node_2.statistics.rx, None)
        self.assertEqual(node_2.statistics.tx, None)
        self.assertEqual(node_2.statistics.forward, None)
        self.assertEqual(node_2.statistics.mgmt_rx, None)
        self.assertEqual(node_2.statistics.mgmt_tx, None)

        self.assertEqual(node_2.nodeinfo.node_id, "c04a00dd692a")
        self.assertEqual(node_2.nodeinfo.location.latitude, 49.83675075)
        self.assertEqual(node_2.nodeinfo.location.longitude, 8.70046645)
        self.assertEqual(node_2.nodeinfo.hardware.model, "TP-Link TL-WDR3600 v1")
        self.assertEqual(node_2.nodeinfo.hardware.nproc, 1)
        self.assertEqual(node_2.nodeinfo.system.site_code, "ffda")
        self.assertEqual(node_2.nodeinfo.hostname, "64367-blockheizkraftwerk")

        self.assertEqual(node_2.nodeinfo.software.autoupdater.enabled, True)
        self.assertEqual(node_2.nodeinfo.software.autoupdater.branch, "stable")

        self.assertEqual(node_2.nodeinfo.software.firmware.base, "gluon-v2017.1.3")
        self.assertEqual(node_2.nodeinfo.software.firmware.release, "1.0.3")
