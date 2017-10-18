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

import os
import paramiko
import time

import rumba.log as log

# Fix Python 2.x.
try:
    input = raw_input
except NameError:
    pass

logger = log.get_logger(__name__)


class SSHException(Exception):
    pass

def get_ssh_client():
    ssh_client = paramiko.SSHClient()
    ssh_client.load_system_host_keys()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    return ssh_client


def _print_stream(stream):
        o = str(stream.read()).strip('b\'\"\\n')
        if o != "":
            o_array = o.split('\\n')
            for oi in o_array:
                logger.debug(oi)
        return o.rstrip()

def ssh_connect(ssh_client, hostname, port, username, password, time_out,
                proxy):
    retry = 0
    max_retries = 10
    while retry < max_retries:
        time.sleep(retry * 5)
        try:
            ssh_client.connect(hostname, port, username, password,
                               look_for_keys=True, timeout=time_out, sock=proxy)
            return
        except (paramiko.ssh_exception.SSHException, EOFError):
            retry += 1
            logger.error('Failed to connect to host, retrying: ' +
                         str(retry) + '/' + str(max_retries) + ' retries')
        except paramiko.ssh_exception.BadHostKeyException:
            retry += 1
            logger.error(hostname + ' has a mismatching entry in ' +
                         '~/.ssh/known_hosts')
            logger.error('If you are sure this is not a man in the ' +
                         'middle attack, edit that file to remove the' +
                         'entry and then hit return to try again.')
            input('Hit Enter when ready')
    if retry == max_retries:
        raise SSHException('Failed to connect to host')

def execute_proxy_commands(testbed, ssh_config, commands, time_out=3):
    """
    Remote execution of a list of shell command on hostname, using the
    http and https proxy specified by the testbed. By
    default this function will exit (timeout) after 3 seconds.

    @param testbed: testbed info
    @param ssh_config: ssh config of the node
    @param commands: *nix shell command
    @param time_out: time_out value in seconds, error will be generated if
    no result received in given number of seconds, the value None can
    be used when no timeout is needed
    """
    new_commands = []
    for command in commands:
        proxy = testbed.http_proxy
        if proxy is not None:
            proxy_command = 'export http_proxy=' + proxy + '; ' \
                            + 'export https_proxy=' + proxy + ';'
            new_commands.append(proxy_command + ' ' + command)
        else:
            new_commands.append(command)
    return execute_commands(testbed, ssh_config, new_commands, time_out)


def execute_proxy_command(testbed, ssh_config, command, time_out=3):
    """
    Remote execution of a list of shell command on hostname, using
    a proxy http and https.
    By default this function will exit (timeout) after 3 seconds.

    @param testbed: testbed info
    @param ssh_config: ssh config of the node
    @param command: *nix shell command
    @param time_out: time_out value in seconds, error will be generated if
    no result received in given number of seconds, the value None can
    be used when no timeout is needed

    @return: stdout resulting from the command
    """
    o = execute_proxy_commands(testbed, ssh_config, [command], time_out)
    if o is not None:
        return o


def execute_commands(testbed, ssh_config, commands, time_out=3):
    """
    Remote execution of a list of shell command on hostname. By
    default this function will exit (timeout) after 3 seconds.

    @param testbed: testbed info
    @param ssh_config: ssh config of the node
    @param commands: *nix shell command
    @param time_out: time_out value in seconds, error will be generated if
    no result received in given number of seconds, the value None can
    be used when no timeout is needed
    """
    if ssh_config.proxy_command is not None:
        proxy = paramiko.ProxyCommand(ssh_config.proxy_command)
    else:
        proxy = None

    ssh_client = get_ssh_client()

    ssh_connect(ssh_client, ssh_config.hostname, ssh_config.port,
                testbed.username, testbed.password, time_out, proxy)

    o = ""
    for command in commands:
        logger.debug("%s@%s:%s >> %s" % (testbed.username,
                                         ssh_config.hostname,
                                         ssh_config.port,
                                         command))
        envars = '. /etc/profile;'
        command = envars + ' ' + command
        chan = ssh_client.get_transport().open_session()
        stdout = chan.makefile()
        try:
            chan.exec_command(command)
        except paramiko.ssh_exception.SSHException as e:
            raise SSHException('Failed to execute command')
        o = _print_stream(stdout)
        if (chan.recv_exit_status() != 0):
            raise SSHException('A remote command returned an error.\n' + o)

    ssh_client.close()
    return o


def execute_command(testbed, ssh_config, command, time_out=3):
    """
    Remote execution of a list of shell command on hostname. By
    default this function will exit (timeout) after 3 seconds.

    @param testbed: testbed info
    @param ssh_config: ssh config of the node
    @param command: *nix shell command
    @param time_out: time_out value in seconds, error will be generated if
    no result received in given number of seconds, the value None can
    be used when no timeout is needed

    @return: stdout resulting from the command
    """
    o = execute_commands(testbed, ssh_config, [command], time_out)
    if o is not None:
        return o


def write_text_to_file(testbed, ssh_config, text, file_name):
    """
    Write a string to a given remote file.
    Overwrite the complete file if it already exists!

    @param testbed: testbed info
    @param ssh_config: ssh config of the node
    @param text: string to be written in file
    @param file_name: file name (including full path) on the host
    """
    ssh_client = get_ssh_client()

    if ssh_config.proxy_command is not None:
        proxy = paramiko.ProxyCommand(ssh_config.proxy_command)
    else:
        proxy = None

    ssh_connect(ssh_client, ssh_config.hostname, ssh_config.port,
                testbed.username, testbed.password, None, proxy)

    cmd = "touch " + file_name + "; chmod a+rwx " + file_name

    try:
        stdin, stdout, stderr = ssh_client.exec_command(cmd)
        del stdin, stdout
        err = str(stderr.read()).strip('b\'\"\\n')
        if err != "":
            logger.error(err)

        sftp_client = ssh_client.open_sftp()
        remote_file = sftp_client.open(file_name, 'w')

        remote_file.write(text)
        remote_file.close()

    except SSHException as e:
        raise SSHException('Failed to write text to remote file')


def copy_files_to_testbed(testbed, ssh_config, paths, destination):
    """
    Copies local files to a remote node.

    @param testbed: testbed info
    @param ssh_config: ssh config of the node
    @param paths: source paths (local) as an iterable
    @param destination: destination folder name (remote)
    """
    ssh_client = get_ssh_client()

    if ssh_config.proxy_command is not None:
        proxy = paramiko.ProxyCommand(ssh_config.proxy_command)
    else:
        proxy = None

    if destination is not '' and not destination.endswith('/'):
        destination = destination + '/'


    ssh_connect(ssh_client, ssh_config.hostname, ssh_config.port,
                testbed.username, testbed.password, None, proxy)

    try:
        sftp_client = ssh_client.open_sftp()

        for path in paths:
            file_name = os.path.basename(path)
            dest_file = destination + file_name
            logger.debug("Copying %s to %s@%s:%s path %s" % (
                path,
                testbed.username,
                ssh_config.hostname,
                ssh_config.port,
                dest_file))
            sftp_client.put(path, dest_file)

    except Exception as e:
        raise SSHException('Failed to copy files to testbed')


def copy_file_to_testbed(testbed, ssh_config, path, destination):
    """
    Copies a local file to a remote node.

    @param testbed: testbed info
    @param ssh_config: ssh config of the node
    @param path: source path (local)
    @param destination: destination folder name (remote)
    """
    copy_files_to_testbed(testbed, ssh_config, [path], destination)


def setup_vlan(testbed, node, vlan_id, int_name):
    """
    Gets the interface (ethx) to link mapping

    @param testbed: testbed info
    @param node: the node to create the VLAN on
    @param vlan_id: the VLAN id
    @param int_name: the name of the interface
    """
    if testbed.username == 'root':
        def sudo(s):
            return s
    else:
        def sudo(s):
            return 'sudo ' + s

    logger.debug("Setting up VLAN on node %s, if %s.", node.name, int_name)

    args = {'ifname': str(int_name), 'vlan': str(vlan_id)}

    cmds = [sudo("ip link add link %(ifname)s name "
                 "%(ifname)s.%(vlan)s type vlan id %(vlan)s"
                 % args),
            sudo("ifconfig %(ifname)s.%(vlan)s up"
                 % args)]
    if testbed.flags['no_vlan_offload']:
        cmds += [sudo("ethtool -K %(ifname)s rxvlan off"
                      % args),
                 sudo("ethtool -K %(ifname)s txvlan off"
                      % args)]
    execute_commands(testbed, node.ssh_config, cmds)
