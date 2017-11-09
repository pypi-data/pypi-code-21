# Copyright (c) 2013 Qumulo, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

import qumulo.lib.opts
import qumulo.lib.util
import qumulo.rest.cluster as cluster

class ListNodesCommand(qumulo.lib.opts.Subcommand):
    NAME = "nodes_list"
    DESCRIPTION = "List nodes"

    @staticmethod
    def options(parser):
        parser.add_argument("--node", help="Node ID")

    @staticmethod
    def main(conninfo, credentials, _args):
        if _args.node is not None:
            print cluster.list_node(conninfo, credentials, _args.node)
        else:
            print cluster.list_nodes(conninfo, credentials)

class GetClusterConfCommand(qumulo.lib.opts.Subcommand):
    NAME = "cluster_conf"
    DESCRIPTION = "Get the cluster config"

    @staticmethod
    def main(conninfo, credentials, _args):
        print cluster.get_cluster_conf(conninfo, credentials)

class SetClusterConfCommand(qumulo.lib.opts.Subcommand):
    NAME = "set_cluster_conf"
    DESCRIPTION = "Set the cluster config"

    @staticmethod
    def options(parser):
        parser.add_argument("--cluster-name", help="Cluster Name",
                            required=True)

    @staticmethod
    def main(conninfo, credentials, _args):
        print cluster.put_cluster_conf(conninfo, credentials,
            _args.cluster_name)

class SetSSLCertificateCommand(qumulo.lib.opts.Subcommand):
    NAME = "ssl_modify_certificate"
    DESCRIPTION = "Set the SSL certificate chain and private key for the " \
                  "web UI and REST servers"

    @staticmethod
    def options(parser):
        parser.add_argument("-c", "--certificate", type=str, required=True,
            help="SSL certificate chain in PEM format. Must contain " \
                 "entire certificate chain up to the root CA")
        parser.add_argument("-k", "--private-key", type=str, required=True,
            help="RSA private key file in PEM format")

    @staticmethod
    def main(conninfo, credentials, args):
        cert, key = None, None

        with open(args.certificate) as cert_f, open(args.private_key) as key_f:
            cert, key = cert_f.read(), key_f.read()

        print cluster.set_ssl_certificate(conninfo, credentials, cert, key)

class SetSSLCACertificateCommand(qumulo.lib.opts.Subcommand):
    NAME = "ssl_modify_ca_certificate"
    DESCRIPTION = "Set SSL CA certificate. This certificate is used to " \
        "authenticate connections to external LDAP servers."

    @staticmethod
    def options(parser):
        parser.add_argument("-c", "--certificate", type=str, required=True,
            help="SSL CA certificate file in PEM format")

    @staticmethod
    def main(conninfo, credentials, args):
        with open(args.certificate) as f:
            cert = f.read()
        print cluster.set_ssl_ca_certificate(conninfo, credentials, cert)

class GetSSLCACertificateCommand(qumulo.lib.opts.Subcommand):
    NAME = "ssl_get_ca_certificate"
    DESCRIPTION = "Get SSL CA certificate. This certificate is used to " \
        "authenticate connections to external LDAP servers."

    @staticmethod
    def main(conninfo, credentials, _args):
        print cluster.get_ssl_ca_certificate(conninfo, credentials)

class DeleteSSLCACertificateCommand(qumulo.lib.opts.Subcommand):
    NAME = "ssl_delete_ca_certificate"
    DESCRIPTION = "Delete SSL CA certificate. This certificate is used to " \
        "authenticate connections to external LDAP servers."

    @staticmethod
    def main(conninfo, credentials, _args):
        print cluster.delete_ssl_ca_certificate(conninfo, credentials)

class GetClusterSlotStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = "cluster_slots"
    DESCRIPTION = "Get the cluster disk slots status"

    @staticmethod
    def options(parser):
        parser.add_argument("--slot", help="Slot ID")

    @staticmethod
    def main(conninfo, credentials, args):
        if args.slot is not None:
            print cluster.get_cluster_slot_status(
                conninfo, credentials, args.slot)
        else:
            print cluster.get_cluster_slots_status(
                conninfo, credentials)

class GetRestriperStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = "restriper_status"
    DESCRIPTION = "Get restriper status"

    @staticmethod
    def main(conninfo, credentials, _args):
        print cluster.get_restriper_status(conninfo, credentials)

class GetProtectionStatusCommand(qumulo.lib.opts.Subcommand):
    NAME = "protection_status_get"
    DESCRIPTION = "Get cluster protection status"

    @staticmethod
    def main(conninfo, credentials, _args):
        print cluster.get_protection_status(conninfo, credentials)

class SetNodeIdentifyLight(qumulo.lib.opts.Subcommand):
    NAME = "set_node_identify_light"
    DESCRIPTION = "Turn node identification light on or off"

    @staticmethod
    def options(parser):
        parser.add_argument("--node", help="Node ID", required=True)
        parser.add_argument("light_state", choices=["on", "off"],
                            help="Should light be visible")

    @staticmethod
    def main(conninfo, credentials, args):
        light_visible = args.light_state == "on"
        print cluster.set_node_identify_light(conninfo, credentials,
                                              args.node, light_visible)

class GetNodeChassisStatus(qumulo.lib.opts.Subcommand):
    NAME = "node_chassis_status_get"
    DESCRIPTION = "Get the status of node chassis"

    @staticmethod
    def options(parser):
        parser.add_argument("--node", help="Node ID")

    @staticmethod
    def main(conninfo, credentials, args):
        print cluster.get_node_chassis_status(conninfo, credentials,
                                              args.node)

class CreateCluster(qumulo.lib.opts.Subcommand):
    NAME = "cluster_create"
    DESCRIPTION = "Creates a Qumulo Cluster"

    @staticmethod
    def options(parser):
        parser.add_argument("--cluster-name", help="Cluster Name",
                            required=True)
        parser.add_argument("--admin-password",
                            help="Administrator Pasword", required=True)
        parser.add_argument("--accept-eula", help="Accept the EULA",
                            dest="accept_eula", action="store_true")
        parser.add_argument("--reject-eula", help="Reject the EULA",
                            dest="accept_eula", action="store_false")

        node_group = parser.add_mutually_exclusive_group(required=True)
        node_group.add_argument("--node-uuids",
            help="Cluster node UUIDs",
            action="append",
            default=[],
            nargs="+")
        node_group.add_argument("--node-ips",
            help="Cluster node IPv4 addresses",
            action="append",
            default=[],
            nargs="+")

    @staticmethod
    def main(conninfo, credentials, args):
        # For backward compatibility, we support multiple instances of
        # --node-uuids to append but we also would like to allow multiple node
        # uuids give to each instance.  Flatten resulting list of lists.
        args.node_uuids = [x for sublist in args.node_uuids for x in sublist]
        args.node_ips = [x for sublist in args.node_ips for x in sublist]

        print cluster.create_cluster(
            conninfo,
            credentials,
            args.cluster_name,
            args.admin_password,
            args.node_uuids,
            args.node_ips,
            args.accept_eula)

class AddNode(qumulo.lib.opts.Subcommand):
    NAME = "add_nodes"
    DESCRIPTION = "Add unconfigured nodes to a Qumulo Cluster"

    @staticmethod
    def options(parser):
        nodes_group = parser.add_mutually_exclusive_group(required=True)
        nodes_group.add_argument("--node-uuids",
                                 help="Unconfigured node uuids to add",
                                 action="append",
                                 nargs="+",
                                 default=[])
        nodes_group.add_argument("--node-ips",
                                 help="Unconfigured node ips to add",
                                 action="append",
                                 nargs="+",
                                 default=[])

    @staticmethod
    def main(conninfo, credentials, args):
        # For backward compatibility, we support multiple instances of
        # --node-uuids to append but we also would like to allow multiple node
        # uuids give to each instance.  Flatten resulting list of lists.
        args.node_uuids = [x for sublist in args.node_uuids for x in sublist]
        args.node_ips = [x for sublist in args.node_ips for x in sublist]

        print cluster.add_node(
            conninfo,
            credentials,
            node_uuids=args.node_uuids,
            node_ips=args.node_ips)
