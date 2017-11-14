#!/usr/bin/env python
from __future__ import print_function, division, unicode_literals, absolute_import
from actappliance.act_errors import act_errors, ACTError
from actappliance.permissions import AppliancePermissions
from actappliance.connections import ApplianceSsh, ApplianceRest
from bitpermissions import PermissionException
import logging
from paramiko import AuthenticationException


appl_types = ['cds', 'sky', 'psky', 'skyng']
appl_types_str = ', '.join(appl_types[:-1]) + ', or ' + appl_types[-1]


class Appliance(object):
    """
    An appliance represents CDS or SKY actifio product.

    As a general rule use cmd method for all udsinfo and udstask commands. This allows them to be changed dynamically
    at runtime. If you are sending a hidden rest command use rest and if you are sending a command that can't be sent
    over rest use raw.

    Usage:
     a = Appliance(ip_address='172.27.4.0'
     r = a.cmd('udsinfo lshost -filtervalue hostname=dog&hosttype=puppey')
     hostid = r.parse(k='id')

    The API for this object is aided by dynamic_keywords. If we call a method with a name matching the conversion
    table in keyword_prefixes, we will attempt to build a simple call and check method. This avoids writing a lot of
    boilerplate and filters all calls through a specific naming convention and methods, so it can be monkeypatched if
    a feature changes or a bug is found.
    """

    def __init__(self, hostname=None, ip_address=None, connection_type='rest', appliance_type=None, version=None,
                 ssh_args=None, rest_params=None):
        """
        Setup config info as well as permissions

        ssh_args should normally have username, password, port as keys.
        rest_params should normally have name, password, vendorkey as keys.

        :param hostname: DNS name of machine to connect to (hostname or ip_address required)
        :param ip_address: Ip address of machine to connect to (hostname or ip_address required)
        :param connection_type: Default way to connect to appliance (options: cli, rest)
        :param appliance_type: Category of appliance
        :param ssh_args: Dictionary of ssh connection args to send to paramiko's connect method
        :param rest_params: Dictionary of connection params to send alongside RESTful requests
        """
        # These permissions are to stop users from hitting unexpected failures. Not for security.
        self.perms = AppliancePermissions()

        self.logger = logging.getLogger(__name__)

        # Get system info
        self.hostname = hostname
        self.ip_address = ip_address
        self.system = ip_address or hostname
        if not self.system:
            self.logger.info('Ip address or hostname required to send commands')

        # Get connection info
        self.ssh_args = ssh_args if ssh_args is not None else {}
        self.rest_params = rest_params if rest_params is not None else {}

        # Get optional appliance type
        self._appliance_type = appliance_type if appliance_type is not None and appliance_type.lower() in appl_types \
            else None
        self._version = version

        # Ensure connection input is valid
        connection_type = connection_type.lower()
        if connection_type in ('rest', 'cli'):
            self.connection_type = connection_type
        else:
            raise ValueError("connection_type accepts 'rest' or 'cli'; {} was given".format(connection_type))

        # Make connections for commands
        self._make_connections()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    def _make_connections(self):
        self.rest_conn = ApplianceRest(self.system, self.rest_params)
        self.ssh_conn = ApplianceSsh(self.system, self.ssh_args)

    def cmd(self, operation, **update_cmds):
        """
        Connect to the machine using the classes connection type and send the given command.

        If an argument needs to be sent in the operation and not in kwargs with argument make sure it is first in the
        series of commands.

        :param operation: CLI-like command to send
        :param update_cmds: add or overwrite commands in the operation. Will not add if value is none.
        :return: ActResponse object
        """
        self.perms.has_cmd()
        if self.connection_type == "rest":
            return self.rest(operation, **update_cmds)
        elif self.connection_type == "cli":
            return self.cli(operation, **update_cmds)
        else:
            raise RuntimeError("Couldn't find suitable cmd method based on connection type. {} "
                               "provided".format(self.connection_type))

    def rest(self, operation, **update_cmds):
        """
        Use when you explicitly want to connect over RESTful API.

        :param operation: CLI-like command to be sent. ex. udsinfo lshost
        :param update_cmds: keyword arguments to be sent with command
        :return:
        """
        self.perms.has_rest()

        return self.rest_conn.cmd(operation, **update_cmds)

    def cli(self, operation, **update_cmds):
        """
        Use when you explicitly want to connect over ssh.

        :param operation: CLI-like command to be sent. ex. udsinfo lshost
        :param update_cmds: keyword arguments to be sent with command
        :return: ActResponse object
        """
        self.perms.has_ssh()

        return self.ssh_conn.cmd(operation, **update_cmds)

    def raw(self, command, *args, **kwargs):
        """
        Use when you explicitly want to connect over ssh and send raw ssh commands.

        This houses the functionality unlike rest method because I want to avoid passing around the client to retain
        channels.
        :param command:
        :return: stdout, stderr, exit status
        """
        self.perms.has_ssh()

        return self.ssh_conn.raw(command, *args, **kwargs)

    def ui_call(self, method, url_suffix, params=None, data=None, **kwargs):
        """
        Used to send Actifio desktop rest calls.

        :param method: type of rest call to make. ie. GET, POST
        :param url_suffix: What follows actifio in the UI call. i.e. https://<some_hostname>/actifio/<url_suffix here>
        :return:
        """
        self.perms.has_rest()
        return self.rest_conn.ui_call(method, url_suffix, params, data, **kwargs)

    def teardown(self):
        self.rest_conn.disconnect()
        self.ssh_conn.disconnect()

    @property
    def appliance_type(self):
        if not self._appliance_type:
            self._appliance_type = self.get_appliance_type()
        return self._appliance_type

    def get_appliance_type(self):
        """Find the appliance's type. ex. sky, cds, skyng"""
        appliance_type = None
        try:
            self.logger.debug("Searching for appliance type over ssh.")
            out, err, rc = self.raw('rpm -qa | grep actsys | grep -ho -e svc -e skyng -e psky -e sky', statuses=[0])
            try:
                actsys_type = out[0].lower()
            except IndexError:
                raise ValueError("rpm actsys didn't return a meaningful type.")
            appliance_type = actsys_type.replace('svc', 'cds')
            if appliance_type not in appl_types:
                msg = "Appliance type {} from rpm -qa isn't {}".format(appliance_type, appl_types_str)
                self.logger.exception(msg)
                raise ValueError(msg)
        except (AuthenticationException, ValueError, PermissionException):
            self.logger.debug("Failed to get appliance type over ssh, searching with RESTful API.")
            r = self.rest('udsinfo lsversion')
            r.raise_for_error()
            for di in r['result']:
                for v in di.values():
                    value = v.lower()
                    if value in appl_types:
                        appliance_type = value
                        break

        appliance_type = appliance_type.replace('psky', 'skyng')
        if appliance_type not in appl_types:
            raise RuntimeError("Invalid appliance type {0} found".format(appliance_type))
        self.logger.info("Appliance type is {}.".format(appliance_type))
        return str(appliance_type)

    @property
    def version(self):
        if not self._version:
            self._version = self.get_version()
        return self._version

    def get_version(self):
        r = self.cmd('udsinfo lsversion')
        version = r.parse(k='version', m_k='component', m_v='srv-revision')
        if not version:
            self.logger.debug('This system looks older and may call srv-revision psrv-revision, attempting to grab.')
            version = r.parse(k='version', m_k='component', m_v='psrv-revision')
        if not version:
            raise RuntimeError("No version found.")
        self.logger.info('srv-version is {}'.format(self._version))
        return version

    def new_user(self, new_name, new_password=None):
        """
        This is an idempotent way to select and sign in as a new user with default rights.

        :param new_name: New username to create or find
        :param new_password: New password to set or use
        :return: New Appliance object with the new user information based off of the current instance
        """
        if new_password is None:
            new_password = self.rest_params.get('password')

        try:
            r = self.cmd('udstask mkuser', name=new_name, password=new_password)
            r.raise_for_error()
        except act_errors[10006]:
            # This assumes the password of the created user is new_password, so we have to check the password works
            self.logger.info('User {} already existed.'.format(new_name))
            check_login = True
        else:
            # we don't need to check_login if exceptions aren't hit
            check_login = False

        # Remove the ssh permissions
        new_perms = self.perms
        new_perms.ssh = False
        # set the new params
        new_rest_params = self.rest_params.copy()
        new_rest_params['name'] = new_name
        new_rest_params['password'] = new_password

        new_args = []
        for arg in [self.hostname, self.ip_address, self.connection_type, self._appliance_type, self.version,
                    self.ssh_args]:
            try:
                new_args.append(arg.copy())
            except AttributeError:
                new_args.append(arg)

        new_appliance = Appliance(*new_args, rest_params=new_rest_params)
        new_appliance.perms = new_perms

        # If we found an existing user, make sure our password works
        if check_login:
            r = new_appliance.rest('udsinfo lsversion')
            try:
                r.raise_for_error()
            except ACTError:
                raise RuntimeError("User {} already existed and the provided password was incorrect.".format(new_name))

        return new_appliance
