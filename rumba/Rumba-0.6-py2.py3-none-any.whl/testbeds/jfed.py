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

import subprocess
import getpass
import xml.dom.minidom as xml
import os.path
import time
import tarfile
import sys

if sys.version_info[0] >= 3:
    from urllib.request import urlretrieve
else:
    from urllib import urlretrieve

import rumba.model as mod
import rumba.log as log
from rumba import ssh_support

logger = log.get_logger(__name__)


class Testbed(mod.Testbed):

    def __init__(self, exp_name, username, cert_file, exp_hours="2",
                 proj_name="ARCFIRE", authority="wall2.ilabt.iminds.be",
                 image=None):
        passwd = getpass.getpass(prompt="Password for certificate file: ")
        mod.Testbed.__init__(self,
                             exp_name,
                             username,
                             passwd,
                             proj_name,
                             http_proxy="https://proxy.atlantis.ugent.be:8080")
        self.authority = "urn:publicid:IDN+" + authority + "+authority+cm"
        self.auth_name = authority
        self.cert_file = cert_file
        self.exp_hours = exp_hours
        self.if_id = dict()
        self.rspec = os.path.join(mod.tmp_dir, self.exp_name + ".rspec")
        self.manifest = os.path.join(mod.tmp_dir, self.exp_name + ".rrspec")
        self.jfed_jar = os.path.join(mod.cache_dir,
                                     'jfed_cli/experimenter-cli.jar')
        if image is not None:
            self.image = "urn:publicid:IDN+" + authority + \
                         "+image+wall2-ilabt-iminds-be:" + image
        else:
            self.image = None

        if not os.path.exists(self.jfed_jar):
            logger.info("Couldn't find jFed CLI. Downloading.")
            tarball = "jfed_cli.tar.gz"
            url = "http://jfed.iminds.be/downloads/stable/jar/" + tarball
            urlretrieve(url, filename=tarball)
            tar = tarfile.open(tarball)
            tar.extractall()
            tar.close()
            os.rename(os.path.join(os.getcwd(), 'jfed_cli'),
                      os.path.join(mod.cache_dir, 'jfed_cli'))
            os.remove(tarball)
        self.flags['no_vlan_offload'] = True

    def create_rspec(self, experiment):
        impl = xml.getDOMImplementation()
        doc = impl.createDocument(None, "rspec", None)

        top_el = doc.documentElement
        top_el.setAttribute("xmlns", "http://www.geni.net/resources/rspec/3")
        top_el.setAttribute("type", "request")
        top_el.setAttribute("xmlns:emulab", "http://www.protogeni.net/" +
                            "resources/rspec/ext/emulab/1")
        top_el.setAttribute("xmlns:jfedBonfire", "http://jfed.iminds.be/" +
                            "rspec/ext/jfed-bonfire/1")
        top_el.setAttribute("xmlns:delay", "http://www.protogeni.net/" +
                            "resources/rspec/ext/delay/1")
        top_el.setAttribute("xmlns:jfed-command", "http://jfed.iminds.be/" +
                            "rspec/ext/jfed-command/1")
        top_el.setAttribute("xmlns:client", "http://www.protogeni.net/" +
                            "resources/rspec/ext/client/1")
        top_el.setAttribute("xmlns:jfed-ssh-keys", "http://jfed.iminds.be/" +
                            "rspec/ext/jfed-ssh-keys/1")
        top_el.setAttribute("xmlns:jfed", "http://jfed.iminds.be/rspec/" +
                            "ext/jfed/1")
        top_el.setAttribute("xmlns:sharedvlan", "http://www.protogeni.net/" +
                            "resources/rspec/ext/shared-vlan/1")
        top_el.setAttribute("xmlns:xsi", "http://www.w3.org/2001/" +
                            "XMLSchema-instance")
        top_el.setAttribute("xsi:schemaLocation", "http://www.geni.net/" +
                            "resources/rspec/3 http://www.geni.net/" +
                            "resources/rspec/3/request.xsd")

        for node in experiment.nodes:
            el = doc.createElement("node")
            top_el.appendChild(el)
            el.setAttribute("client_id", node.name)
            el.setAttribute("exclusive", "true")
            el.setAttribute("component_manager_id", self.authority)

            el2 = doc.createElement("sliver_type")
            el.appendChild(el2)
            el2.setAttribute("name", "raw-pc")

            if self.image is not None:
                image_el = doc.createElement("disk_image")
                image_el.setAttribute("name", self.image)
                el2.appendChild(image_el)

            node.ifs = 0
            for ipcp in node.ipcps:
                if isinstance(ipcp, mod.ShimEthIPCP):
                    el3 = doc.createElement("interface")
                    self.if_id[ipcp] = node.name + ":if" + str(node.ifs)
                    el3.setAttribute("client_id", self.if_id[ipcp])
                    node.ifs += 1
                    el.appendChild(el3)

        for dif in experiment.dif_ordering:
            if isinstance(dif, mod.ShimEthDIF):
                el = doc.createElement("link")
                top_el.appendChild(el)
                el.setAttribute("client_id", dif.name)

                el2 = doc.createElement("component_manager_id")
                el2.setAttribute("name", self.authority)
                el.appendChild(el2)

                for ipcp in dif.ipcps:
                    el3 = doc.createElement("interface_ref")
                    el3.setAttribute("client_id", self.if_id[ipcp])
                    el.appendChild(el3)

        file = open(self.rspec, "w")
        file.write(doc.toprettyxml())
        file.close()

    def swap_out(self, experiment):
        subprocess.call(["java", "-jar", self.jfed_jar, "delete", "-S",
                         self.proj_name, "-s",
                         self.exp_name, "-p", self.cert_file,
                         "-P", self.password])

    def swap_in(self, experiment):
        self.create_rspec(experiment)

        for node in experiment.nodes:
            auth_name_r = self.auth_name.replace(".", "-")
            node.ssh_config.hostname = \
                node.name + "." + self.exp_name + "." + \
                auth_name_r + "." + self.auth_name
            node.ssh_config.proxy_command = "ssh -i '" + self.cert_file + \
                                            "' -o StrictHostKeyChecking=no " + \
                                            self.username + \
                                            "@bastion.test.iminds.be nc " + \
                                            node.ssh_config.hostname + " 22"
            node.ssh_config.username = self.username
            node.ssh_config.password = self.password

        subprocess.call(["java", "-jar", self.jfed_jar, "create", "-S",
                         self.proj_name, "--rspec",
                         self.rspec, "-s",
                         self.exp_name, "-p", self.cert_file, "-k",
                         "usercert,userkeys,shareduserallkeys",
                         "--create-slice",
                         "--manifest", self.manifest,
                         "-P", self.password,
                         "-e", self.exp_hours])

        rspec = xml.parse(self.manifest)
        xml_nodes = rspec.getElementsByTagName("node")

        # Complete details of the nodes after swapin
        logger.info("Sleeping for two seconds to avoid contacting jfed nodes "
                    "too soon.")
        time.sleep(2)
        for xml_node in xml_nodes:
            n_name = xml_node.getAttribute("client_id")
            intfs = xml_node.getElementsByTagName("interface")

            got = False
            for node in experiment.nodes:
                if node.name == n_name:
                    node_n = node
                    got = True
            if not got:
                logger.error("Not found node %s", n_name)

            for intf in intfs:
                aux_mac_address = intf.getAttribute("mac_address")
                mac = ":".join(
                    [aux_mac_address[i:i+2] for i in range(0, 12, 2)]
                )
                command = (
                    'echo "mac=\\"\$1\\"; cd / && ./sbin/ifconfig -a | '
                    'awk \'/^[a-z]/ { if ( \\"\'\\"\$mac\\"\'\\" == \$5 )'
                    ' print \$1}\'" > mac2ifname.sh')
                ssh_support.execute_command(self, node_n.ssh_config, command)

                # ssh_support.copy_path_to_testbed(
                #     self,
                #     node_n.ssh_config,
                #     os.path.join(dir_path, 'mac2ifname.sh'),
                #     '')
                ssh_support.execute_command(
                    self,
                    node_n.ssh_config,
                    'cd ~ && chmod a+x mac2ifname.sh')
                ifname = ssh_support.execute_command(
                    self,
                    node_n.ssh_config,
                    './mac2ifname.sh ' + mac
                )
                i_name = intf.getAttribute("client_id")
                for ipcp in node_n.ipcps:
                    if isinstance(ipcp, mod.ShimEthIPCP):
                        if self.if_id[ipcp] == i_name:
                            ipcp.ifname = ifname
                            if ifname is None:
                                logger.error("Could not determine name of node"
                                             "%s interface %s"
                                             % (node_n.name, mac))
                            else:
                                logger.debug("Node %s interface %s has name %s."
                                             % (node_n.name, mac, ifname))
                            # comp_id = intf.getAttribute("component_id")
                            # comp_arr = comp_id.split(":")
                            # ipcp.ifname = comp_arr[-1]
                            # xml_ip = intf.getElementsByTagName("ip")
                            # interface.ip = xml_ip[0].getAttribute("address")
