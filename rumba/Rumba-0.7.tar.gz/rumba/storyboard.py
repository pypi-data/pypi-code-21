#
# A library to manage ARCFIRE experiments
#
#    Copyright (C) 2017 Nextworks S.r.l.
#    Copyright (C) 2017 imec
#
#    Sander Vrijders   <sander.vrijders@ugent.be>
#    Dimitri Staessens <dimitri.staessens@ugent.be>
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

# Base class for client apps
#
# @ap: Application Process binary
# @options: Options to pass to the binary
#
import os
import random
import time

import rumba.model as model
import rumba.ssh_support as ssh_support
import rumba.log as log

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

current_id = -1


def get_id():
    global current_id
    current_id += 1
    return current_id


class Client(object):
    def __init__(self, ap, nodes=None, options=None, shutdown="kill <pid>"):
        self.ap = ap
        self.startup = (ap + ((" " + options) if options is not None else ""))
        if isinstance(nodes, model.Node):
            nodes = [nodes]
        elif nodes is None:
            nodes = []
        self.nodes = nodes
        self.shutdown = shutdown

    def add_node(self, node):
        if not isinstance(node, model.Node):
            raise Exception("A Node is required.")
        self.nodes.append(node)

    def process(self, duration):
        node = random.choice(self.nodes) if len(self.nodes) > 0 else None
        return ClientProcess(get_id(), self.ap, self.startup, duration, node, self.shutdown)


# Base class for client processes
#
# @ap: Application Process binary
# @duration: The time (in seconds) this process should run
# @start_time: The time at which this process is started.
# @options: Options to pass to the binary
#
class ClientProcess(object):
    def __init__(self, client_id, ap, startup, duration,
                 node=None, shutdown="<kill <pid>"):
        self.id = client_id
        self.ap = ap
        self.startup = startup
        self.duration = duration
        self.start_time = None
        self.running = False
        self.node = node
        self.pid = None
        self.shutdown = shutdown

    def run(self, node=None):
        if node is not None:
            self.node = node
        if self.node is None:
            raise Exception('No node specified for client %s' % (self.ap,))
        self.start_time = time.time()

        logger.debug(
            'Starting client app %s on node %s with duration %s.',
            self.ap, self.node.name, self.duration
        )

        start_cmd = "./startup.sh %s_%s %s" % (
            self.ap,
            self.id,
            self.startup.replace("<duration>", str(self.duration)),
        )
        self.running = True
        try:
            self.pid = self.node.execute_command(start_cmd)
        except ssh_support.SSHException:
            logger.warning('Could not start client %s on node %s.',
                           self.ap, self.node.name)
        logger.debug('Client app %s on node %s got pid %s.',
                     self.ap, self.node.name, self.pid)

    def stop(self):
        if self.shutdown != "":
            logger.debug(
                'Killing client %s on node %s.',
                self.ap, self.node.name
            )
            try:
                kill_cmd = self.shutdown.replace('<pid>', str(self.pid))
                self.node.execute_command(kill_cmd)
            except ssh_support.SSHException:
                    logger.warn('Could not kill client %s on node %s.',
                                self.ap, self.node.name)
        else:
            logger.debug(
                'Client %s on node %s has terminated.',
                self.ap, self.node.name
            )

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
        self.options = options if options is not None else ""
        self.max_clients = max_clients
        if clients is None:
            clients = list()
        self.clients = clients
        if nodes is None:
            nodes = []
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
        return [self.make_client_process() for _ in range(number)]

    def make_client_process(self):
        """Returns a client of this server"""
        if len(self.clients) == 0:
            raise Exception("Server %s has empty client list." % (self,))
        duration = exponential(self.mean_duration)
        return random.choice(self.clients).process(
            duration=float("%.2f" % (duration,))
        )

    def run(self):
        for node in self.nodes:
            logfile = "%s_server.log" % self.ap
            script = r'nohup "$@" > %s 2>&1 & echo "$!"' % (logfile,)
            run_cmd = self.ap + (
                (" " + self.options) if self.options is not None else ""
            )
            cmd_1 = "echo '%s' > startup.sh && chmod a+x startup.sh" \
                    % (script,)
            cmd_2 = "./startup.sh %s" % (run_cmd,)
            logger.debug(
                'Starting server %s on node %s with logfile %s.',
                self.ap, node.name, logfile
            )
            try:
                node.execute_command(cmd_1)
                self.pids[node] = (node.execute_command(cmd_2))
            except ssh_support.SSHException:
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
            except ssh_support.SSHException:
                logger.warn('Could not kill server %s on node %s.',
                            self.ap, node.name)


# Base class for ARCFIRE storyboards
#
# @experiment: Experiment to use as input
# @duration: Duration of the whole storyboard
# @servers: App servers available in the network.
#           Type == Server or Type == List[Tuple[Server, Node]]
#
class StoryBoard:

    DEFAULT_INTERVAL = 2.5  # in seconds (may be a float)

    def __init__(self, duration, experiment=None, servers=None):
        self.experiment = experiment
        self.duration = duration
        self.servers = list()
        if servers is None:
            servers = list()
        for s in servers:
            self._validate_and_add_server(s)
        self.active_clients = []
        self.start_time = None

    def _validate_and_add_server(self, s):
        if self.experiment is None:
            raise ValueError("Cannot add a server before "
                             "setting the experiment.")
        if hasattr(s, '__len__') and len(s) == 2:
            server, node = s
            if not isinstance(server, Server) \
                    or not isinstance(node, model.Node):
                raise TypeError('First element must be of "Server" type, '
                                'second must be of "Node" type.')
            server.add_node(node)
            self.servers.append(server)
        elif type(s) == Server:
            self.servers.append(s)
        else:
            raise TypeError('Input servers should be either an object of '
                            '"Server" type or a Server-Node couple.')
        for node in self.servers[-1].nodes:
            if node not in self.experiment.nodes:
                raise ValueError('Cannot run server on node %s, '
                                 'not in experiment.' % (node.name,))

    def set_experiment(self, experiment):
        if not isinstance(experiment, model.Experiment):
            raise TypeError('Experiment instance required.')
        self.experiment = experiment

    def add_server(self, server):
        self._validate_and_add_server(server)

    def del_server(self, server):
        self.servers.remove(server)

    def start(self):
        self.start_time = time.time()
        script = r'logname="$1"; shift; nohup "${@}" ' \
                 r'> /tmp/${logname}.rumba.log 2>&1  & echo "$!"'
        logger.debug("Writing utility startup script on client nodes.")
        for server in self.servers:
            for client in server.clients:
                for node in client.nodes:
                    node.execute_command(
                        "echo '%s' > startup.sh && chmod a+x startup.sh"
                        % (script,)
                    )
        try:
            for server in self.servers:
                server.run()
            while time.time() - self.start_time < self.duration:
                for server in self.servers:
                    clients = server.get_new_clients(self.DEFAULT_INTERVAL)
                    for new_client in clients:
                        new_client.run()
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

    def fetch_logs(self, local_dir='.'):
        if not os.path.isdir(local_dir):
            raise Exception('"%s" is not a directory. Cannot fetch logs.'
                            % local_dir)
        server_nodes = set()
        client_nodes = set()
        for server in self.servers:
            for node in server.nodes:
                server_nodes.add(node)
            for client in server.clients:
                for node in client.nodes:
                    client_nodes.add(node)
        for node in server_nodes:
            logs_list = node.execute_command('ls *_server.log')
            logger.info('Log list is:\n%s', logs_list)
            node.fetch_files(logs_list.split('\n'), local_dir)
        for node in client_nodes:
            logs_list = node.execute_command('ls /tmp/*.rumba.log '
                                             '|| echo ""')
            logger.info('Log list is:\n%s', logs_list)
            node.fetch_files(logs_list.split('\n'), local_dir)
