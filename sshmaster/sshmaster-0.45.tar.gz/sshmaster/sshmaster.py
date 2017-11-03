#!/usr/bin/env python
import os
import paramiko
import sys
from types import *
import vmtools
import time
from gmailer.gmailer import senderror_simple
from scp import SCPClient
from paramiko.ssh_exception import NoValidConnectionsError
from io import StringIO

vm_root_path = vmtools.vm_root_grabber()
sys.path.append(vm_root_path)
import pkgutil
local_settings_present = pkgutil.find_loader('local_settings')
if local_settings_present:
    from local_settings import *

def create_remote_file(current_host, username, file_location, file_contents, file_mode, keyfile=None, key_string=None, file_owner='default', port=22, use_sudo=False, print_stdout=True):
    """runs a commad via ssh on the host: current_host and returns a dictionary of the results
    :type current_host: string
    :param current_host: the host you want to run your command on
    :type username: string
    :param username: the username to use when connecting
    :type keyfile: string
    :param keyfile: the absolute local path to the private ssh key (Note: either keyfile or key_string must be provided, if both are provided, key_string will be tried first)
    :type file_location: string
    :param file_location: the absolute path of the remote file to create
    :type file_contents: string
    :param file_contents: the contents of the file to create
    :type file_mode: int
    :param file_mode: the octal number number representing the new permissions for the file as used by chmod (ex 755)
    :type file_owner: string
    :param file_owner: the owner of the new file (if the special value 'default' is used the OS default will be use, usually the ssh username)
    :type port: intr
    :param port: the port to connect on
    :type use_sudo: boolean
    :param use_sudo: Wether to prefix all commands with 'sudo'
    :type print_stdout: boolean
    :param print_stdout: Wether to print the stdout to terminal (this can be helpful for debuging)
    """
    # build the command_dictionary
    command_dict = {}
    command_dict['create_file_command'] = """bash -c 'echo "{}" > {}'""".format(file_contents, file_location)
    command_dict['file_mode_command'] = 'chmod {} {}'.format(str(file_mode), file_location)
    command_dict['file_owner_command'] = 'chown {}:{} {}'.format(file_owner, file_owner, file_location)
    # tac on sudo if requested
    if use_sudo:
        for dict_key in command_dict:
            command_dict[dict_key] = 'sudo {}'.format(command_dict[dict_key])
        
    # create file
    ssh_cmd(current_host=current_host, command=command_dict['create_file_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout)
    # execute file mode
    ssh_cmd(current_host=current_host, command=command_dict['file_mode_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout)
    # change owners if requested
    if file_owner != 'default':
        ssh_cmd(current_host=current_host, command=command_dict['file_owner_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout)

def create_remote_file_multi_try(current_host, username, file_location, file_contents, file_mode, keyfile=None, key_string=None, file_owner='default', port=22, use_sudo=False, print_stdout=True, trys=10, debug=False):
    """runs a commad via ssh on the host: current_host and returns a dictionary of the results
    :type current_host: string
    :param current_host: the host you want to run your command on
    :type username: string
    :param username: the username to use when connecting
    :type keyfile: string
    :param keyfile: the absolute local path to the private ssh key (Note: either keyfile or key_string must be provided, if both are provided, key_string will be tried first)
    :type file_location: string
    :param file_location: the absolute path of the remote file to create
    :type file_contents: string
    :param file_contents: the contents of the file to create
    :type file_mode: int
    :param file_mode: the octal number number representing the new permissions for the file as used by chmod (ex 755)
    :type file_owner: string
    :param file_owner: the owner of the new file (if the special value 'default' is used the OS default will be use, usually the ssh username)
    :type port: intr
    :param port: the port to connect on
    :type use_sudo: boolean
    :param use_sudo: Wether to prefix all commands with 'sudo'
    :type print_stdout: boolean
    :param print_stdout: Wether to print the stdout to terminal (this can be helpful for debuging)
    :type trys: int
    :param trys: the number of times to try to connect
    :type debug: boolean
    :param debug: Wether to print debug info (maybe help to turn on print_stdout too)
    """
    # build the command_dictionary
    command_dict = {}
    command_dict['create_file_command'] = """bash -c 'echo "{}" > {}'""".format(file_contents, file_location)
    command_dict['file_mode_command'] = 'chmod {} {}'.format(str(file_mode), file_location)
    command_dict['file_owner_command'] = 'chown {}:{} {}'.format(file_owner, file_owner, file_location)
    # tac on sudo if requested
    if use_sudo:
        for dict_key in command_dict:
            command_dict[dict_key] = 'sudo {}'.format(command_dict[dict_key])
        
    # create file
    ssh_cmd_multi_try(current_host=current_host, command=command_dict['create_file_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout, trys=trys, debug=debug)
    # execute file mode
    ssh_cmd_multi_try(current_host=current_host, command=command_dict['file_mode_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout, trys=trys, debug=debug)
    # change owners if requested
    if file_owner != 'default':
        ssh_cmd_multi_try(current_host=current_host, command=command_dict['file_owner_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout, trys=trys, debug=debug)


def scp_cmd(current_host, mode, username, local_file, remote_file, keyfile=None, key_string=None, recursive=False, preserve_times=False, port=22, file_owner='default', file_mode='default', use_sudo=False, print_stdout=True, trys=10, debug=False):
    """put or get a file via scp
    :type current_host: string
    :param current_host: the remote host to copy to or from
    :type mode: string
    :param mode: put or get
    :type local_file: string
    :param local_file: the absolute path to the local file
    :type remote_file: string
    :param remote_file: the absolute path to the remote file
    :type recursive: boolean
    :param recursive: boolean option False if a single file True if a directory
    :type preserve_times: boolean
    :param preserve_times: boolean option False if no True if yes
    :type username: string
    :param username: the username to use when connecting
    :type keyfile: string
    :param keyfile: the absolute local path to the private ssh key (Note: either keyfile or key_string must be provided, if both are provided, key_string will be tried first)
    :type port: intr
    :param port: the port to connect on
    :type file_mode: int
    :param file_mode: the octal number number representing the new permissions for the file as used by chmod (ex 755) (if the special value 'default' is used the OS default will be used, based on umask)
    :type file_owner: string
    :param file_owner: the owner of the new file (if the special value 'default' is used the OS default will be used, usually the ssh username)
    :type use_sudo: boolean
    :param use_sudo: Wether to prefix all commands with 'sudo'
    :type print_stdout: boolean
    :param print_stdout: Wether to print the stdout to terminal for the commands to execute file mode, owner, etc commands (this can be helpful for debuging)
    :type trys: int
    :param trys: the number of times to try on the commands to execute file mode, owner, etc commands
    :type debug: boolean
    :param debug: Wether to print debug info (maybe help to turn on print_stdout too)
    """
    # temp path only used if use_sudo is True
    temp_remote_path='/tmp/temp_{}'.format(remote_file.split('/')[-1])
    # build the command_dictionary
    command_dict = {}
    command_dict['file_move_command'] = "mv {} {}".format(temp_remote_path, remote_file)
    command_dict['file_mode_command'] = 'chmod {} {}'.format(str(file_mode), remote_file)
    command_dict['file_owner_command'] = 'chown {}:{} {}'.format(file_owner, file_owner, remote_file)
    # tac on sudo if requested
    if use_sudo:
        for dict_key in command_dict:
            command_dict[dict_key] = 'sudo {}'.format(command_dict[dict_key])
    # make the paramiko connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(current_host, username=username, key_filename=keyfile, port=port )
    scp = SCPClient(ssh.get_transport())
    # push the file up
    if mode == 'put':
        if use_sudo:
            scp.put(files=local_file, remote_path=temp_remote_path, recursive=recursive, preserve_times=preserve_times)
            # move file to permanent location
            ssh_cmd_multi_try(current_host=current_host, command=command_dict['file_move_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout, trys=trys, debug=debug)
            # execute file mode if requested
            if file_mode != 'default':
                ssh_cmd_multi_try(current_host=current_host, command=command_dict['file_mode_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout, trys=trys, debug=debug)
            # change owners if requested
            if file_owner != 'default':
                ssh_cmd_multi_try(current_host=current_host, command=command_dict['file_owner_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout, trys=trys, debug=debug)
        else:
            scp.put(files=local_file, remote_path=remote_file, recursive=recursive, preserve_times=preserve_times)
            # execute file mode if requested
            if file_mode != 'default':
                ssh_cmd_multi_try(current_host=current_host, command=command_dict['file_mode_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout, trys=trys, debug=debug)
            # change owners if requested
            if file_owner != 'default':
                ssh_cmd_multi_try(current_host=current_host, command=command_dict['file_owner_command'], username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout, trys=trys, debug=debug)
    # pull file down
    if mode == 'get':
        scp.get(remote_path=remote_file, local_path=local_file, recursive=recursive, preserve_times=preserve_times)

def scp_cmd_multi_try(current_host, mode, username, local_file, remote_file, keyfile=None, key_string=None, recursive=False, preserve_times=False, port=22, file_owner='default', file_mode='default', print_stdout=True, trys=10, use_sudo=False, debug=False):
    """sends or gets a file via scp, try 
    :type current_host: string
    :param current_host: the remote host to copy to or from
    :type mode: string
    :param mode: put or get
    :type local_file: string
    :param local_file: the absolute path to the local file
    :type remote_file: string
    :param keyfile: the absolute local path to the private ssh key (Note: either keyfile or key_string must be provided, if both are provided, key_string will be tried first)
    :type recursive: boolean
    :param recursive: boolean option False if a single file True if a directory
    :type preserve_times: boolean
    :param preserve_times: boolean option False if no True if yes
    :type username: string
    :param username: the username to use when connecting
    :type keyfile: string
    :param keyfile: the absolute path to the private ssh key
    :type port: intr
    :param port: the port to connect on
    :type print_stdout: boolean
    :param print_stdout: Wether to print the stdout to terminal for the commands to execute file mode, owner, etc commands (this can be helpful for debuging)
    :type trys: int
    :param trys: the number of times to try to connect
    :type debug: boolean
    :param debug: Wether to print debug info (maybe help to turn on print_stdout too)
    """
    actual_trys = 1
    while actual_trys != trys:
        if debug:
            attempts_message = 'scp attempt {} of {}'.format(actual_trys, trys)
            print(attempts_message)
        try:
            scp_cmd(current_host=current_host, mode=mode, username=username, keyfile=keyfile, local_file=local_file, remote_file=remote_file, recursive=recursive, preserve_times=preserve_times, port=port, file_owner=file_owner, file_mode=file_mode, use_sudo=use_sudo, trys=trys, debug=debug )
        except (NoValidConnectionsError)  as e:
        # should we catch socket.errors too?
        #except (NoValidConnectionsError, socket.error)  as e:
            time.sleep(5)
            actual_trys += 1
        else:
            if debug:
                success_message = 'scp success: uploaded local file {} to {} on host {}'.format(local_file, remote_file, current_host)
                print(success_message)
            break
    if actual_trys == trys:
        raise NoValidConnectionsError(e)
        # does ths raise the last error?
        #raise
        

# function for running a shell command on a host
def ssh_cmd(current_host, command, username, keyfile=None, key_string=None, port=22, print_stdout=True, use_sudo=False):
    """runs a commad via ssh on the host: current_host and returns a dictionary of the results
    :type current_host: string
    :param current_host: the host you want to run your command on
    :type command: string
    :param command: the command you wish to run
    :type username: string
    :param username: the username to use when connecting
    :type keyfile: string
    :param keyfile: the absolute local path to the private ssh key (Note: either keyfile or key_string must be provided, if both are provided, key_string will be tried first)
    :type key_string: string
    :param key_string: the private ssh key in string format (Note: either keyfile or key_string must be provided, if both are provided, key_string will be tried first)
    :type port: intr
    :param port: the port to connect on
    :type print_stdout: boolean
    :param print_stdout: Wether to print the stdout to terminal (this can be helpful for debuging)
    :type use_sudo: boolean
    :param use_sudo: Wether to prefix all commands with 'sudo'
    """
    # if we have a key_string convert to pkey object
    if key_string:
        key_file_object = StringIO(key_string)
        pkey_object = paramiko.RSAKey.from_private_key(key_file_object)
    else:
        pkey_object = None

    # make sure command ends in a new line
    if not command.endswith('\n'):
        command = '{}\n'.format(command)
    # tac on sudo if requested
    if use_sudo:
        command = 'sudo {}'.format(command)
    # establish our dict for returning
    ssh_cmd_dict = {}
    # fill in the stuff we know
    #ssh_cmd_dict['server'] = current_host
    ssh_cmd_dict['current_host'] = current_host
    ssh_cmd_dict['command'] = command
    # make the ssh object
    ssh = paramiko.SSHClient()
    # add new servers to known_hosts automatically
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # try to establish the connection to server
    try:
        ssh.connect(current_host, username=username, pkey=pkey_object, key_filename=keyfile, port=port )
    except:
        # record connection failure
        ssh_cmd_dict['connection_successful'] = False
        # if it doesn't work tell 'em
        print('unable to connect to: '+current_host)
        return ssh_cmd_dict
    else:
        # record connection success
        ssh_cmd_dict['connection_successful'] = True
        # execute the command storing stdout, stdin, and stderr
        stdin, stdout, stderr = ssh.exec_command(command)
        # wait for the end of line from stdout so we know the command has finished
        while not stdout.channel.eof_received:
            time.sleep(3)
        # wait for exit status (that means command finished)
        exit_status = stdout.channel.recv_exit_status()
        # flush commands and cut off more writes
        stdin.flush()
        stdin.channel.shutdown_write()

        # close the connection
        ssh.close()

        # store the stdout
        ssh_cmd_dict['stdout_raw'] = stdout.readlines()

        # create an entry that is pretty to read
        if isinstance(ssh_cmd_dict['stdout_raw'], list):
            ssh_cmd_dict['stdout_print'] = "".join(ssh_cmd_dict['stdout_raw'])
        ssh_cmd_dict['stdout'] = ssh_cmd_dict['stdout_raw']

        # store stdin
        ssh_cmd_dict['stdin'] = command

        # store the stderr
        ssh_cmd_dict['stderr_raw'] = stderr.readlines()
        # create an entry for stderr that is pretty to read
        if isinstance(ssh_cmd_dict['stderr_raw'], list):
            ssh_cmd_dict['stderr_print'] = "".join(ssh_cmd_dict['stderr_raw'])
        ssh_cmd_dict['stderr'] = ssh_cmd_dict['stderr_raw']

        # store exit status
        ssh_cmd_dict['exitstatus'] = exit_status

        if exit_status > 0:
            if ssh_cmd_dict['stderr'] is not None:
                print('Unfortunately the command: '+command+' executed on server: '+current_host+' had a non-zero exit status. Below is the stderr:')
                print(ssh_cmd_dict['stderr'])
        else:
            if print_stdout:
                if ssh_cmd_dict['stdout_print'] is not None:
                    print(ssh_cmd_dict['stdout_print'])
        return ssh_cmd_dict

def ssh_cmd_multi_try(current_host, command, username, keyfile=None, key_string=None, port=22, print_stdout=True, use_sudo=False, trys=10, debug=False):
    """runs a commad via ssh on the host: current_host and returns a dictionary of the results, and trys multiple times
    :type current_host: string
    :param current_host: the host you want to run your command on
    :type command: string
    :param command: the command you wish to run
    :type username: string
    :param username: the username to use when connecting
    :type keyfile: string
    :param keyfile: the absolute local path to the private ssh key (Note: either keyfile or key_string must be provided, if both are provided, key_string will be tried first)
    :type port: intr
    :param port: the port to connect on
    :type print_stdout: boolean
    :param print_stdout: Wether to print the stdout to terminal (this can be helpful for debuging)
    :type use_sudo: boolean
    :param use_sudo: Wether to prefix all commands with 'sudo'
    :type trys: int
    :param trys: the number of times to try to connect
    :type debug: boolean
    :param debug: Wether to print debug info (maybe help to turn on print_stdout too)
    """
    actual_trys = 1
    while actual_trys != trys:
        if debug:
            attempts_message = 'ssh attempt {} of {}'.format(actual_trys, trys)
            print(attempts_message)
        try:
            ssh_cmd(current_host=current_host, command=command, username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=print_stdout, use_sudo=use_sudo)
        except (NoValidConnectionsError)  as e:
        # should we catch socket.errors too?
        #except (NoValidConnectionsError, socket.error)  as e:
            time.sleep(5)
            actual_trys += 1
        else:
            if debug:
                success_message = 'ssh success: executed command {} on host {}'.format(command, current_host)
                print(success_message)
            break
    if actual_trys == trys:
        raise NoValidConnectionsError(e)
        # does ths raise the last error?
        #raise


def ssh_cmd_auto_check(current_host, command, username, keyfile=None, key_string=None, port=22, print_stdout=True, use_sudo=False):
    """runs a commad via ssh on the host: current_host and returns a dictionary of the results, if the connection is not successful or the exitstatus is non-zero send an email to error recipients and exit with an error
    :type current_host: string
    :param current_host: the host you want to run your command on
    :type command: string
    :param command: the command you wish to run
    :type username: string
    :param username: the username to use when connecting
    :type keyfile: string
    :param keyfile: the absolute local path to the private ssh key (Note: either keyfile or key_string must be provided, if both are provided, key_string will be tried first)
    :type port: intr
    :param port: the port to connect on
    :type print_stdout: boolean
    :param print_stdout: Wether to print the stdout to terminal (this can be helpful for debuging)
    :type use_sudo: boolean
    :param use_sudo: Wether to prefix all commands with 'sudo'
    """
    ssh_cmd_output = ssh_cmd(current_host, command, username=username, keyfile=keyfile, key_string=key_string, port=port, print_stdout=True, use_sudo=use_sudo)
    if not ssh_cmd_output['connection_successful'] or ssh_cmd_output['exitstatus'] != 0:
        subject_text="command executed on %s failed " % current_host
        body_text = "Executed on: %s\nCommand: %s\nConnection_successful: %s\nStdout: %s\nStderr: %s\nExit Status: %s\n" %( current_host, ssh_cmd_output['command'], ssh_cmd_output['connection_successful'], ssh_cmd_output['stdout_print'], ssh_cmd_output['stderr_print'], ssh_cmd_output['exitstatus'])
        senderror_simple(subject_text, body_text)
        print(body_text)
        sys.exit(1)
    return ssh_cmd_output

