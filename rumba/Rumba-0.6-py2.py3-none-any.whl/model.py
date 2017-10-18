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

import abc
import os
import random
import stat
import time

import rumba.log as log
from rumba import ssh_support
from rumba.ssh_support import SSHException

logger = log.get_logger(__name__)

try:
    from numpy.random import poisson
    from numpy.random import exponential
    logger.debug("Using numpy for faster and better random variables.")
except ImportError:
    from rumba.recpoisson import poisson

    def exponential(mean_duration):
        return random.expovariate(1.0 / mean_duration)

    logger.debug("Falling back to simple implementations.")
    # PROBLEM! These logs will almost never be printed... But we might not care

tmp_dir = '/tmp/rumba'
try:
    os.mkdir(tmp_dir)
    os.chmod(tmp_dir, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
except OSError:
    # Already there, nothing to do
    pass

cache_parent_dir = os.path.join(os.path.expanduser("~"), '.cache/')
try:
    os.mkdir(cache_parent_dir)
except OSError:
    # Already there, nothing to do
    pass
cache_dir = os.path.join(os.path.expanduser("~"), '.cache/rumba/')
try:
    os.mkdir(cache_dir)
except OSError:
    # Already there, nothing to do
    pass


# Represents generic testbed info
#
# @username [string] user name
# @password [string] password
# @proj_name [string] project name
# @exp_name [string] experiment name
#
class Testbed:
    def __init__(self,
                 exp_name,
                 username,
                 password,
                 proj_name,
                 http_proxy=None):
        self.username = username
        self.password = password
        self.proj_name = proj_name
        self.exp_name = exp_name
        self.http_proxy = http_proxy
        self.flags = {'no_vlan_offload': False}

    @abc.abstractmethod
    def swap_in(self, experiment):
        raise Exception('swap_in() not implemented')

    @abc.abstractmethod
    def swap_out(self, experiment):
        logger.info("swap_out(): nothing to do")


# Base class for DIFs
#
# @name [string] DIF name
#
class DIF:
    def __init__(self, name, members=None):
        self.name = name
        if members is None:
            members = list()
        self.members = members
        self.ipcps = list()

    def __repr__(self):
        s = "DIF %s" % self.name
        return s

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other is not None and self.name == other.name

    def __neq__(self, other):
        return not self == other

    def add_member(self, node):
        self.members.append(node)

    def del_member(self, node):
        self.members.remove(node)

    def get_ipcp_class(self):
        return IPCP


# Shim over UDP
#
class ShimUDPDIF(DIF):
    def __init__(self, name, members=None):
        DIF.__init__(self, name, members)

    def get_ipcp_class(self):
        return ShimUDPIPCP


# Shim over Ethernet
#
# @link_speed [int] Speed of the Ethernet network, in Mbps
#
class ShimEthDIF(DIF):
    def __init__(self, name, members=None, link_speed=0):
        DIF.__init__(self, name, members)
        self.link_speed = int(link_speed)
        if self.link_speed < 0:
            raise ValueError("link_speed must be a non-negative number")

    def get_ipcp_class(self):
        return ShimEthIPCP


# Normal DIF
#
# @policies [dict] Policies of the normal DIF. Format:
#       dict( componentName: str --> comp_policy:
#               dict( policy_name: str --> parameters:
#                       dict( name: str --> value: str )))
#
class NormalDIF(DIF):
    def __init__(self, name, members=None, policy=None):
        DIF.__init__(self, name, members)
        if policy is None:
            policy = Policy(self)
        self.policy = policy

    def add_policy(self, comp, pol, **params):
        self.policy.add_policy(comp, pol, **params)

    def del_policy(self, comp=None, policy_name=None):
        self.policy.del_policy(comp, policy_name)

    def show(self):
        s = DIF.__repr__(self)
        for comp, pol_dict in self.policy.get_policies().items():
            for pol, params in pol_dict.items():
                s += "\n       Component %s has policy %s with params %s" \
                     % (comp, pol, params)
        return s


# SSH Configuration
#
class SSHConfig:
    def __init__(self, hostname, port=22, proxy_command=None):
        self.username = None
        self.password = None
        self.hostname = hostname
        self.port = port
        self.proxy_command = proxy_command

    def set_username(self, username):
        self.username = username

    def set_password(self, password):
        self.password = password


# A node in the experiment
#
# @difs: DIFs the node will have an IPCP in
# @dif_registrations: Which DIF is registered in which DIF
# @policies: dict of dif -> policy to apply for that dif in this node
#
#
class Node:
    def __init__(self, name, difs=None, dif_registrations=None,
                 client=False, policies=None):
        self.name = name
        if difs is None:
            difs = list()
        self.difs = difs
        for dif in self.difs:
            dif.add_member(self)
        if dif_registrations is None:
            dif_registrations = dict()
        self.dif_registrations = dif_registrations
        self.ssh_config = SSHConfig(name)
        self.ipcps = []
        self.policies = dict()
        if policies is None:
            policies = dict()
        for dif in self.difs:
            if hasattr(dif, 'policy'):  # check if the dif supports policies
                self.policies[dif] = policies.get(dif, Policy(dif, self))
        self.client = client

        self._validate()

    def get_ipcp_by_dif(self, dif):
        for ipcp in self.ipcps:
            if ipcp.dif == dif:
                return ipcp

    def _undeclared_dif(self, dif):
        if dif not in self.difs:
            raise Exception("Invalid registration: node %s is not declared "
                            "to be part of DIF %s" % (self.name, dif.name))

    def _validate(self):
        # Check that DIFs referenced in self.dif_registrations
        # are part of self.difs
        for upper in self.dif_registrations:
            self._undeclared_dif(upper)
            for lower in self.dif_registrations[upper]:
                self._undeclared_dif(lower)

    def __repr__(self):
        s = "Node " + self.name + ":\n"

        s += "  DIFs: [ "
        s += " ".join([d.name for d in self.difs])
        s += " ]\n"

        s += "  DIF registrations: [ "
        rl = []
        for upper in self.dif_registrations:
            difs = self.dif_registrations[upper]
            x = "%s => [" % upper.name
            x += " ".join([lower.name for lower in difs])
            x += "]"
            rl.append(x)
        s += ", ".join(rl)
        s += " ]\n"

        return s

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return other is not None and self.name == other.name

    def __neq__(self, other):
        return not self == other

    def add_dif(self, dif):
        self.difs.append(dif)
        dif.add_member(self)
        if hasattr(dif, 'policy'):
            self.policies[dif] = Policy(dif, self)
        self._validate()

    def del_dif(self, dif):
        self.difs.remove(dif)
        dif.del_member(self)
        try:
            del self.policies[dif]
        except KeyError:
            # It was not in there, so nothing to do
            pass
        self._validate()

    def add_dif_registration(self, upper, lower):
        self.dif_registrations[upper].append(lower)
        self._validate()

    def del_dif_registration(self, upper, lower):
        self.dif_registrations[upper].remove(lower)
        self._validate()

    def add_policy(self, dif, component_name, policy_name, **parameters):
        self.policies[dif].add_policy(component_name, policy_name, **parameters)

    def del_policy(self, dif, component_name=None, policy_name=None):
        self.policies[dif].del_policy(component_name, policy_name)

    def get_policy(self, dif):
        return self.policies[dif]

    def execute_commands(self, commands, time_out=3, use_proxy=False):
        # Ssh_config is used twice since it doubles as testbed info
        # (it holds fields username and password)
        if use_proxy:
            return ssh_support.execute_proxy_commands(
                self.ssh_config,
                self.ssh_config,
                commands,
                time_out
            )
        # else:
        return ssh_support.execute_commands(
            self.ssh_config,
            self.ssh_config,
            commands,
            time_out
        )

    def execute_command(self, command, time_out=3, use_proxy=False):
        # Ssh_config is used twice since it doubles as testbed info
        # (it holds fields username and password)
        if use_proxy:
            return ssh_support.execute_proxy_command(
                self.ssh_config,
                self.ssh_config,
                command,
                time_out
            )
        # else:
        return ssh_support.execute_command(
                self.ssh_config,
                self.ssh_config,
                command,
                time_out
        )

    def write_text_to_file(self, text, file_name):
        ssh_support.write_text_to_file(
            self.ssh_config,
            self.ssh_config,
            text,
            file_name
        )

    def copy_file(self, path, destination):
        ssh_support.copy_file_to_testbed(
            self.ssh_config,
            self.ssh_config,
            path,
            destination
        )

    def copy_files(self, paths, destination):
        ssh_support.copy_files_to_testbed(
            self.ssh_config,
            self.ssh_config,
            paths,
            destination
        )

    def setup_vlan(self, vlan_id, int_name):
        ssh_support.setup_vlan(
            self.ssh_config,
            self.ssh_config,
            vlan_id,
            int_name
        )


# Base class representing an IPC Process to be created in the experiment
#
# @name [string]: IPCP name
# @node: Node where the IPCP gets created
# @dif: the DIF the IPCP belongs to
#
class IPCP:
    def __init__(self, name, node, dif):
        self.name = name
        self.node = node
        self.dif = dif
        self.registrations = []

        # Is this IPCP the first in its DIF, so that it does not need
        # to enroll to anyone ?
        self.dif_bootstrapper = False

    def __repr__(self):
        return "{IPCP=%s,DIF=%s,N-1-DIFs=(%s)%s}" % \
                (self.name, self.dif.name,
                 ' '.join([dif.name for dif in self.registrations]),
                 ',bootstrapper' if self.dif_bootstrapper else ''
                 )

    def __hash__(self):
        return hash((self.name, self.dif.name))

    def __eq__(self, other):
        return other is not None and self.name == other.name \
                                and self.dif == other.dif

    def __neq__(self, other):
        return not self == other


class ShimEthIPCP(IPCP):
    def __init__(self, name, node, dif, ifname=None):
        IPCP.__init__(self, name, node, dif)
        self.ifname = ifname


class ShimUDPIPCP(IPCP):
    def __init__(self, name, node, dif):
        IPCP.__init__(self, name, node, dif)
        # TODO: add IP and port


# Class representing DIF and Node policies
#
# @dif: the dif this policy is applied to.
# @node: the node
#
class Policy(object):
    def __init__(self, dif, node=None, policies=None):
        self.dif = dif  # type: NormalDIF
        self.node = node
        if policies is None:
            self._dict = dict()
        else:
            self._dict = policies

    def add_policy(self, component_name, policy_name, **parameters):
        self._dict.setdefault(component_name, dict())[policy_name] = parameters

    #
    # Fetches effective policy info
    #
    def get_policies(self, component_name=None, policy_name=None):
        policy = self._superimpose()
        if component_name is None:
            return policy._dict
        elif policy_name is None:
            return policy._dict[component_name]
        else:
            return policy._dict[component_name][policy_name]

    def del_policy(self, component_name=None, policy_name=None):
        if component_name is None:
            self._dict = dict()
        elif policy_name is None:
            del self._dict[component_name]
        else:
            del self._dict[component_name][policy_name]

    #
    # Merges this policy into that of its dif, obtaining
    # the effective policy acting on self.node.
    #
    def _superimpose(self):
        if self.node is None:
            return self
        other = self.dif.policy
        base = dict(other._dict)
        base.update(self._dict)
        return Policy(self.dif, self.node, base)

    def __eq__(self, other):
        if not isinstance(other, Policy):
            return False
        else:
            return other.dif == self.dif \
                   and other.node == self.node \
                   and other._dict == self._dict

    def __str__(self):
        node_str = (" Node: " + self.node) if self.node is not None else ""
        return "Policy[Dif: %(dif)s,%(node_str)s Dict: %(dict)s]" \
               % {"dif": self.dif, "node_str": node_str, "dict": self._dict}

    def __repr__(self):
        node_str = (" Node: " + self.node) if self.node is not None else ""
        s = "Policy[ Dif: %(dif)s,%(node_str)s" \
            % {"dif": self.dif, "node_str": node_str}
        comps = []
        for component in self._dict:
            for policy in self._dict[component]:
                comps.append("\n  Component %s has policy %s with params %s"
                             % (component,
                                policy,
                                self._dict[component][policy]))
        s += ",".join(comps)
        s += "\n]\n"
        return s


# Base class for ARCFIRE experiments
#
# @name [string] Name of the experiment
# @nodes: Nodes in the experiment
#
class Experiment:
    def __init__(self, testbed, nodes=None):
        if nodes is None:
            nodes = list()
        self.nodes = nodes
        self.testbed = testbed
        # the strategy employed for completing the enrollment phase in
        # the different DIFs
        self.enrollment_strategy = 'minimal'  # 'full-mesh', 'manual'
        # the strategy employed for setting up the data transfer
        # networks in the DIFs after enrollment
        self.dt_strategy = 'full-mesh'  # 'minimal', 'manual'
        self.dif_ordering = []
        self.enrollments = []  # a list of per-DIF lists of enrollments
        self.dt_flows = [] # a list of per-DIF lists of data transfer flows
        self.mgmt_flows = [] # a list of per-DIF lists of management flows

        # Generate missing information
        self.generate()

    def __repr__(self):
        s = ""
        for n in self.nodes:
            s += "\n" + str(n)

        return s

    def add_node(self, node):
        self.nodes.append(node)
        self.generate()

    def del_node(self, node):
        self.nodes.remove(node)
        self.generate()

    # Compute registration/enrollment order for DIFs
    def compute_dif_ordering(self):
        # Compute DIFs dependency graph, as both adjacency and incidence list.
        difsdeps_adj = dict()
        difsdeps_inc = dict()

        for node in self.nodes:
            for dif in node.difs:
                if dif not in difsdeps_adj:
                    difsdeps_adj[dif] = set()

            for upper in node.dif_registrations:
                for lower in node.dif_registrations[upper]:
                    if upper not in difsdeps_inc:
                        difsdeps_inc[upper] = set()
                    if lower not in difsdeps_inc:
                        difsdeps_inc[lower] = set()
                    if upper not in difsdeps_adj:
                        difsdeps_adj[upper] = set()
                    if lower not in difsdeps_adj:
                        difsdeps_adj[lower] = set()
                    difsdeps_inc[upper].add(lower)
                    difsdeps_adj[lower].add(upper)

        # Kahn's algorithm below only needs per-node count of
        # incident edges, so we compute these counts from the
        # incidence list and drop the latter.
        difsdeps_inc_cnt = dict()
        for dif in difsdeps_inc:
            difsdeps_inc_cnt[dif] = len(difsdeps_inc[dif])
        del difsdeps_inc

        # Init difsdeps_inc_cnt for those DIFs that do not
        # act as lower IPCPs nor upper IPCPs for registration
        # operations
        for node in self.nodes:
            for dif in node.difs:
                if dif not in difsdeps_inc_cnt:
                    difsdeps_inc_cnt[dif] = 0

        # Run Kahn's algorithm to compute topological
        # ordering on the DIFs graph.
        frontier = set()
        self.dif_ordering = []
        for dif in difsdeps_inc_cnt:
            if difsdeps_inc_cnt[dif] == 0:
                frontier.add(dif)

        while len(frontier):
            cur = frontier.pop()
            self.dif_ordering.append(cur)
            for nxt in difsdeps_adj[cur]:
                difsdeps_inc_cnt[nxt] -= 1
                if difsdeps_inc_cnt[nxt] == 0:
                    frontier.add(nxt)
            difsdeps_adj[cur] = set()

        circular_set = [dif for dif in difsdeps_inc_cnt
                        if difsdeps_inc_cnt[dif] != 0]
        if len(circular_set):
            raise Exception("Fatal error: The specified DIFs topology"
                            "has one or more"
                            "circular dependencies, involving the following"
                            " DIFs: %s" % circular_set)

        logger.debug("DIF topological ordering: %s", self.dif_ordering)

    # Compute all the enrollments, to be called after compute_dif_ordering()
    def compute_enrollments(self):
        dif_graphs = dict()
        self.enrollments = []
        self.mgmt_flows = []
        self.dt_flows = []

        for dif in self.dif_ordering:
            neighsets = dict()
            dif_graphs[dif] = dict()
            first = None

            # For each N-1-DIF supporting this DIF, compute the set of nodes
            # that share such N-1-DIF. This set will be called the 'neighset' of
            # the N-1-DIF for the current DIF.

            for node in self.nodes:
                if dif in node.dif_registrations:
                    dif_graphs[dif][node] = []  # init for later use
                    if first is None:  # pick any node for later use
                        first = node
                    for lower_dif in node.dif_registrations[dif]:
                        if lower_dif not in neighsets:
                            neighsets[lower_dif] = []
                        neighsets[lower_dif].append(node)

            # Build the graph, represented as adjacency list
            for lower_dif in neighsets:
                # Each neighset corresponds to a complete (sub)graph.
                for node1 in neighsets[lower_dif]:
                    for node2 in neighsets[lower_dif]:
                        if node1 != node2:
                            dif_graphs[dif][node1].append((node2, lower_dif))

            self.enrollments.append([])
            self.dt_flows.append([])
            self.mgmt_flows.append([])

            if first is None:
                # This is a shim DIF, nothing to do
                continue

            er = []
            for node in dif_graphs[dif]:
                for edge in dif_graphs[dif][node]:
                    er.append("%s --[%s]--> %s" % (node.name,
                                                   edge[1].name,
                                                   edge[0].name))
            logger.debug("DIF graph for %s: %s", dif, ', '.join(er))

            # To generate the list of mgmt flows, minimal enrollments
            # and minimal dt flows, we simulate it, using
            # breadth-first traversal.
            enrolled = {first}
            frontier = {first}
            while len(frontier):
                cur = frontier.pop()
                for edge in dif_graphs[dif][cur]:
                    if edge[0] not in enrolled:
                        enrolled.add(edge[0])
                        enrollee = edge[0].get_ipcp_by_dif(dif)
                        assert(enrollee is not None)
                        enroller = cur.get_ipcp_by_dif(dif)
                        assert(enroller is not None)
                        if self.enrollment_strategy == 'minimal':
                            self.enrollments[-1].append({'dif': dif,
                                                         'enrollee': enrollee,
                                                         'enroller': enroller,
                                                         'lower_dif': edge[1]})
                        self.mgmt_flows[-1].append({'src': enrollee,
                                                    'dst': enroller})
                        if self.dt_strategy == 'minimal':
                            self.dt_flows[-1].append({'src': enrollee,
                                                      'dst': enroller})
                        frontier.add(edge[0])
            if len(dif.members) != len(enrolled):
                raise Exception("Disconnected DIF found: %s" % (dif,))

            # In case of a full mesh enrollment or dt flows
            for cur in dif_graphs[dif]:
                for edge in dif_graphs[dif][cur]:
                    if cur.name < edge[0].name:
                        enrollee = cur.get_ipcp_by_dif(dif)
                        assert(enrollee is not None)
                        enroller = edge[0].get_ipcp_by_dif(dif)
                        assert(enroller is not None)
                        if self.enrollment_strategy == 'full-mesh':
                            self.enrollments[-1].append({'dif': dif,
                                                         'enrollee': enrollee,
                                                         'enroller': enroller,
                                                         'lower_dif': edge[1]})
                        if self.dt_strategy == 'full-mesh':
                            self.dt_flows[-1].append({'src': enrollee,
                                                      'dst': enroller})

            if not (self.dt_strategy == 'minimal'
                    or self.dt_strategy == 'full-mesh') \
                    or not (self.enrollment_strategy == 'full-mesh'
                            or self.enrollment_strategy == 'minimal'):
                # This is a bug
                assert False

        log_string = "Enrollments:\n"
        for el in self.enrollments:
            for e in el:
                log_string += ("    [%s] %s --> %s through N-1-DIF %s\n"
                               % (e['dif'],
                                  e['enrollee'].name,
                                  e['enroller'].name,
                                  e['lower_dif']))
        logger.debug(log_string)

    def compute_ipcps(self):
        # For each node, compute the required IPCP instances, and associated
        # registrations
        for node in self.nodes:
            node.ipcps = []
            # We want also the node.ipcps list to be generated in
            # topological ordering
            for dif in self.dif_ordering:
                if dif not in node.difs:
                    continue

                # Create an instance of the required IPCP class
                ipcp = dif.get_ipcp_class()(
                    name='%s.%s' % (dif.name, node.name),
                    node=node, dif=dif)

                if dif in node.dif_registrations:
                    for lower in node.dif_registrations[dif]:
                        ipcp.registrations.append(lower)

                node.ipcps.append(ipcp)
                dif.ipcps.append(ipcp)

    def compute_bootstrappers(self):
        for node in self.nodes:
            for ipcp in node.ipcps:
                ipcp.dif_bootstrapper = True
                for el in self.enrollments:
                    for e in el:
                        if e['dif'] != ipcp.dif:
                            # Skip this DIF
                            break
                        if e['enrollee'] == ipcp:
                            ipcp.dif_bootstrapper = False
                            # Exit the loops
                            break
                    if not ipcp.dif_bootstrapper:
                        break

    def dump_ssh_info(self):
        f = open(os.path.join(tmp_dir, 'ssh_info'), 'w')
        for node in self.nodes:
            f.write("%s;%s;%s;%s;%s\n" % (node.name,
                                          self.testbed.username,
                                          node.ssh_config.hostname,
                                          node.ssh_config.port,
                                          node.ssh_config.proxy_command))
        f.close()

    # Examine the nodes and DIFs, compute the registration and enrollment
    # order, the list of IPCPs to create, registrations, ...
    def generate(self):
        self.compute_dif_ordering()
        self.compute_ipcps()
        self.compute_enrollments()
        self.compute_bootstrappers()
        for node in self.nodes:
            logger.info("IPCPs for node %s: %s", node.name, node.ipcps)

    @abc.abstractmethod
    def install_prototype(self):
        raise Exception('install_prototype() method not implemented')

    @abc.abstractmethod
    def bootstrap_prototype(self):
        raise Exception('bootstrap_prototype() method not implemented')

    @abc.abstractmethod
    def prototype_name(self):
        raise Exception('prototype_name() method not implemented')

    def swap_in(self):
        # Realize the experiment testbed (testbed-specific)
        self.testbed.swap_in(self)
        self.dump_ssh_info()

    def swap_out(self):
        # Undo the testbed (testbed-specific)
        self.testbed.swap_out(self)


# Base class for client programs
#
# @ap: Application Process binary
# @options: Options to pass to the binary
#
class Client(object):
    def __init__(self, ap, options=None):
        self.ap = ap
        self.options = options

    def start_process(self, duration):
        return ClientProcess(self.ap, duration, self.options)


# Base class for client processes
#
# @ap: Application Process binary
# @duration: The time (in seconds) this process should run
# @start_time: The time at which this process is started.
# @options: Options to pass to the binary
#
class ClientProcess(Client):
    def __init__(self, ap, duration, options=None):
        super(ClientProcess, self).__init__(ap, options=options)
        self.duration = duration
        self.start_time = None
        self.running = False
        self.node = None
        self.pid = None

    def run(self, node):
        self.node = node
        self.start_time = time.time()

        logger.debug(
            'Starting client app %s on node %s with duration %s.',
            self.ap, self.node.name, self.duration
        )

        opt_str = self.options if self.options is not None else ""
        cmd = "./startup.sh %s %s" % (self.ap, opt_str)
        self.running = True
        try:
            self.pid = self.node.execute_command(cmd)
        except SSHException:
            logger.warn('Could not start client %s on node %s.',
                        self.ap, node.name)
        logger.debug('Client app %s on node %s got pid %s.',
                     self.ap, self.node.name, self.pid)

    def stop(self):
        logger.debug(
            'Killing client %s on node %s.',
            self.ap, self.node.name
        )
        try:
            self.node.execute_command("kill %s" % self.pid)
        except SSHException:
                logger.warn('Could not kill client %s on node %s.',
                            self.ap, self.node.name)

    def check(self):
        """Check if the process should keep running, stop it if not,
        and return true if and only if it is still running."""
        now = time.time()
        if not self.running:
            return False
        if now - self.start_time >= self.duration:
            self.stop()
            self.running = False
            return False
        return True


# Base class for server programs
#
# @ap: Application Process binary
# @arrival_rate: Average requests/s to be received by this server
# @mean_duration: Average duration of a client connection (in seconds)
# @options: Options to pass to the binary
# @max_clients: Maximum number of clients to serve
# @clients: Client binaries that will use this server
# @nodes: Specific nodes to start this server on
#
class Server:
    def __init__(self, ap, arrival_rate, mean_duration,
                 options=None, max_clients=float('inf'),
                 clients=None, nodes=None):
        self.ap = ap
        self.options = options
        self.max_clients = max_clients
        if clients is None:
            clients = list()
        self.clients = clients
        self.nodes = nodes
        self.arrival_rate = arrival_rate  # mean requests/s
        self.mean_duration = mean_duration  # in seconds
        self.pids = {}

    def add_client(self, client):
        self.clients.append(client)

    def del_client(self, client):
        self.clients.remove(client)

    def add_node(self, node):
        self.nodes.append(node)

    def del_node(self, node):
        self.nodes.remove(node)

    def get_new_clients(self, interval):
        """
        Returns a list of clients of size appropriate to the server's rate.

        The list's size should be a sample from Poisson(arrival_rate) over
        interval seconds.
        Hence, the average size should be interval * arrival_rate.
        """
        number = poisson(self.arrival_rate * interval)
        number = int(min(number, self.max_clients))
        l = [self.make_client_process() for _ in range(number)]
        return l

    def make_client_process(self):
        """Returns a client of this server"""
        if len(self.clients) == 0:
            raise Exception("Server %s has empty client list." % (self,))
        duration = exponential(self.mean_duration)
        return random.choice(self.clients)\
            .start_process(duration=duration)

    def run(self):
        for node in self.nodes:
            opt_str = self.options if self.options is not None else ""
            logfile = "%s.log" % self.ap
            script = r'nohup "$@" > %s & echo "$!"' % logfile
            cmds = ["echo '%s' > startup.sh && chmod a+x startup.sh"
                    % (script,),
                    "./startup.sh %s %s" % (self.ap, opt_str)]
            logger.debug(
                'Starting server %s on node %s with logfile %s.',
                self.ap, node.name, logfile
            )
            try:
                self.pids[node] = (node.execute_commands(cmds))
            except SSHException:
                logger.warn('Could not start server %s on node %s.',
                            self.ap, node.name)

    def stop(self):
        for node, pid in self.pids.items():
            logger.debug(
                'Killing server %s on node %s.',
                self.ap, node.name
            )
            try:
                node.execute_command("kill %s" % pid)
            except SSHException:
                logger.warn('Could not kill server %s on node %s.',
                            self.ap, node.name)


# Base class for ARCFIRE storyboards
#
# @experiment: Experiment to use as input
# @duration: Duration of the whole storyboard
# @servers: App servers available in the network
#
class StoryBoard:

    DEFAULT_INTERVAL = 2.5  # in seconds (may be a float)

    def __init__(self, experiment, duration, servers=None):
        self.experiment = experiment
        self.duration = duration
        if servers is None:
            servers = list()
        self.servers = servers
        self.client_nodes = [c for c in experiment.nodes if c.client]
        self.active_clients = []
        self.start_time = None

    def add_server(self, server):
        self.servers.append(server)

    def del_server(self, server):
        self.servers.remove(server)

    def start(self):
        self.start_time = time.time()
        script = r'nohup "$@" > /dev/null & echo "$!"'
        for node in self.client_nodes:
            logger.debug("Writing utility startup script on client nodes.")
            node.execute_command(
                "echo '%s' > startup.sh && chmod a+x startup.sh" % (script,)
            )
        try:
            for server in self.servers:
                server.run()
            while time.time() - self.start_time < self.duration:
                for server in self.servers:
                    clients = server.get_new_clients(self.DEFAULT_INTERVAL)
                    for new_client in clients:
                        client_node = random.choice(self.client_nodes)
                        new_client.run(client_node)
                        self.active_clients.append(new_client)
                surviving = []
                for x in self.active_clients:
                    if x.check():
                        surviving.append(x)
                self.active_clients = surviving
                time.sleep(self.DEFAULT_INTERVAL)
        finally:
            for client in self.active_clients:
                client.stop()
            for server in self.servers:
                server.stop()
