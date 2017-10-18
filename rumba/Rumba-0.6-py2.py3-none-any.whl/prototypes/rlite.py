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
import rumba.log as log

import time


logger = log.get_logger(__name__)


# An experiment over the rlite implementation
class Experiment(mod.Experiment):

    def __init__(self, testbed, nodes=None):
        mod.Experiment.__init__(self, testbed, nodes)

    def prototype_name(self):
        return 'rlite'

    def execute_commands(self, node, cmds):
        ssh.execute_commands(self.testbed, node.ssh_config,
                             cmds, time_out=None)

    def execute_proxy_commands(self, node, cmds):
        ssh.execute_proxy_commands(self.testbed, node.ssh_config,
                                   cmds, time_out=None)

    # Prepend sudo to all commands if the user is not 'root'
    def may_sudo(self, cmds):
        if self.testbed.username != 'root':
            for i in range(len(cmds)):
                cmds[i] = "sudo %s" % cmds[i]

    def init_nodes(self):
        # Load kernel modules and start the uipcps daemon
        cmds = ["modprobe rlite",
                "modprobe rlite-normal",
                "modprobe rlite-shim-eth",
                "modprobe rlite-shim-udp4",
                "modprobe rlite-shim-loopback",
                "rlite-uipcps -v DBG &> uipcp.log &"]
        self.may_sudo(cmds)

        for node in self.nodes:
            self.execute_commands(node, cmds)

    def create_ipcps(self):
        for node in self.nodes:
            cmds = []

            for ipcp in node.ipcps:
                # Generate the command to create the IPCP
                if isinstance(ipcp.dif, mod.NormalDIF):
                    ipcp_type = 'normal'
                elif isinstance(ipcp.dif, mod.ShimEthDIF):
                    ipcp_type = 'shim-eth'
                elif isinstance(ipcp.dif, mod.ShimUDPDIF):
                    ipcp_type = 'shim-udp4'
                else:
                    logger.warning(
                        "unknown type for DIF %s, default to loopback",
                        ipcp.dif.name)
                    ipcp_type = 'shim-loopback'

                cmds.append("rlite-ctl ipcp-create %s %s %s" %
                            (ipcp.name, ipcp_type, ipcp.dif.name))

                # Generate the command to configure the interface
                # name for the shim-eth
                if isinstance(ipcp.dif, mod.ShimEthDIF):
                    cmds.append("rlite-ctl ipcp-config %s netdev %s"
                                % (ipcp.name, ipcp.ifname))

                if isinstance(ipcp.dif, mod.NormalDIF) \
                        and ipcp.dif_bootstrapper:
                    cmds.append("rlite-ctl ipcp-enroller-enable %s"
                                % (ipcp.name))

            self.may_sudo(cmds)
            self.execute_commands(node, cmds)

    def register_ipcps(self):
        for node in self.nodes:
            cmds = []

            for ipcp in node.ipcps:
                for lower in ipcp.registrations:
                    cmds.append("rlite-ctl ipcp-register %s %s"
                                % (ipcp.name, lower.name))

            self.may_sudo(cmds)
            self.execute_commands(node, cmds)

    def enroll_ipcps(self):
        for el in self.enrollments:
            for e in el:
                d = {'enrollee': e['enrollee'].name,
                     'dif': e['dif'].name,
                     'lower_dif': e['lower_dif'].name,
                     'enroller': e['enroller'].name
                     }
                cmd = "rlite-ctl ipcp-enroll %(enrollee)s %(dif)s "\
                      "%(lower_dif)s %(enroller)s" % d
                cmds = [cmd]
                self.may_sudo(cmds)
                self.execute_commands(e['enrollee'].node, cmds)
                time.sleep(1)

    def install_prototype(self):
        logger.info("installing rlite on all nodes")
        cmds = ["sudo apt-get update",
                "sudo -E apt-get install g++ gcc cmake "
                "linux-headers-$(uname -r) "
                "protobuf-compiler libprotobuf-dev git --yes",
                "rm -rf ~/rlite",
                "cd ~; git clone https://github.com/vmaffione/rlite",
                "cd ~/rlite && ./configure && make && sudo make install",
                "cd ~/rlite && sudo make depmod"
                ]

        for node in self.nodes:
            self.execute_proxy_commands(node, cmds)
        logger.info("installation complete")

    def bootstrap_prototype(self):
        logger.info("setting up")
        self.init_nodes()
        logger.info("software initialized on all nodes")
        self.create_ipcps()
        logger.info("IPCPs created on all nodes")
        self.register_ipcps()
        logger.info("IPCPs registered to their lower DIFs on all nodes")
        self.enroll_ipcps()
        logger.info("enrollment completed in all DIFs")
