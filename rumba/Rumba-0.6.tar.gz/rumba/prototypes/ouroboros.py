#
# A library to manage ARCFIRE experiments
#
#    Copyright (C) 2017 Nextworks S.r.l.
#    Copyright (C) 2017 imec
#
#    Sander Vrijders   <sander.vrijders@ugent.be>
#    Vincenzo Maffione <v.maffione@nextworks.it>
#    Marco Capitani    <m.capitani@nextworks.it>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., http://www.fsf.org/about/contact/.
#

import rumba.ssh_support as ssh
import rumba.model as mod
import time
import rumba.log as log


logger = log.get_logger(__name__)


# An experiment over the Ouroboros implementation
class Experiment(mod.Experiment):
    def __init__(self, testbed, nodes=None):
        mod.Experiment.__init__(self, testbed, nodes)

    def prototype_name(self):
        return 'ouroboros'

    def setup_ouroboros(self):
        for node in self.nodes:
            ssh.execute_command(self.testbed, node.ssh_config,
                                "sudo nohup irmd > /dev/null &",
                                time_out=None)

    def install_ouroboros(self):
        cmds = list()

        cmds.append("sudo apt-get update")
        cmds.append("sudo apt-get install cmake protobuf-c-compiler " +
                    "git libfuse-dev --yes")
        cmds.append("sudo rm -r ~/ouroboros/build")
        cmds.append("cd ~/ouroboros; sudo ./install_debug.sh /")

        for node in self.nodes:
            ssh.execute_commands(self.testbed, node.ssh_config,
                                 cmds, time_out=None)

    def create_ipcps(self):
        for node in self.nodes:
            cmds = list()
            for ipcp in node.ipcps:
                cmds2 = list()
                if ipcp.dif_bootstrapper:
                    cmd = "irm i b n " + ipcp.name
                else:
                    cmd = "irm i c n " + ipcp.name

                if isinstance(ipcp.dif, mod.ShimEthDIF):
                    # NOTE: Here to test with fake testbed
                    if ipcp.ifname is None:
                        ipcp.ifname = "eth0"
                    cmd += " type shim-eth-llc if_name " + ipcp.ifname
                    cmd += " dif " + ipcp.dif.name
                elif isinstance(ipcp.dif, mod.NormalDIF):
                    cmd += " type normal"
                    if ipcp.dif_bootstrapper:
                        cmd += " dif " + ipcp.dif.name
                        cmd2 = "irm b i " + ipcp.name + " name " + ipcp.dif.name
                        cmds2.append(cmd2)
                        cmd2 = "irm r n " + ipcp.name
                        for dif_b in node.dif_registrations[ipcp.dif]:
                            cmd2 += " dif " + dif_b.name
                        cmds2.append(cmd2)
                        cmd2 = "irm r n " + ipcp.dif.name
                        for dif_b in node.dif_registrations[ipcp.dif]:
                            cmd2 += " dif " + dif_b.name
                        cmds2.append(cmd2)
                elif isinstance(ipcp.dif, mod.ShimUDPDIF):
                    # FIXME: Will fail, since we don't keep IPs yet
                    cmd += " type shim-udp"
                    cmd += " dif " + ipcp.dif.name
                else:
                    logger.error("Unsupported IPCP type")
                    continue

                cmds.append(cmd)
                for cmd in cmds2:
                    cmds.append(cmd)

            ssh.execute_commands(self.testbed, node.ssh_config, cmds,
                                 time_out=None)

    def enroll_ipcps(self):
        for el in self.enrollments:
            for e in el:
                ipcp = e['enrollee']
                cmds = list()
                cmd = "irm i e n " + ipcp.name + " dif " + e['dif'].name
                cmds.append(cmd)
                cmd = "irm b i " + ipcp.name + " name " + ipcp.dif.name
                cmds.append(cmd)
                cmd = "irm r n " + ipcp.name
                for dif_b in e['enrollee'].node.dif_registrations[ipcp.dif]:
                    cmd += " dif " + dif_b.name
                cmds.append(cmd)
                cmd = "irm r n " + ipcp.dif.name
                for dif_b in e['enrollee'].node.dif_registrations[ipcp.dif]:
                    cmd += " dif " + dif_b.name
                cmds.append(cmd)

                ssh.execute_commands(self.testbed,
                                     e['enrollee'].node.ssh_config,
                                     cmds, time_out=None)

    def setup_flows(self, flows):
        for el in flows:
            for e in el:
                ipcp = e['src']
                if flows == self.mgmt_flows:
                    comp = 'mgmt'
                elif flows == self.dt_flows:
                    comp = 'dt'
                else:
                    assert(False)

                cmd = "irm i conn n " + ipcp.name + " comp " + \
                      comp + " dst " + e['dst'].name
                ssh.execute_command(self.testbed,
                                    ipcp.node.ssh_config,
                                    cmd, time_out=None)

    def install_prototype(self):
        logger.info("Installing Ouroboros...")
        self.install_ouroboros()
        logger.info("Installed on all nodes...")

    def bootstrap_prototype(self):
        logger.info("Starting IRMd on all nodes...")
        self.setup_ouroboros()
        logger.info("Creating IPCPs")
        self.create_ipcps()
        logger.info("Enrolling IPCPs...")
        self.enroll_ipcps()
        logger.info("Setting up management flows...")
        self.setup_flows(self.mgmt_flows)
        logger.info("Setting up data transfer flows...")
        self.setup_flows(self.dt_flows)
        logger.info("All done, have fun!")
