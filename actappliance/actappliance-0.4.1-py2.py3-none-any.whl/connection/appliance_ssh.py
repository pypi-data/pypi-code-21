import logging
import paramiko
import re
import atexit
import signal

from actappliance.connections.connection import ApplianceConnection


class ApplianceSsh(ApplianceConnection):

    def __init__(self, system, call_timeout=6 * 60 * 60, **connect_args):
        super(ApplianceSsh, self).__init__()
        self.logger = logging.getLogger(__name__)

        self.system = system
        self.connect_args = connect_args
        self.call_timeout = call_timeout
        # SSH delimiter to use during uds commands
        self.SSH_DELIM = '|MiLeD|'

        # set in method 'connect'
        self.ssh_client = None

    def connect(self):
        """
        Connect to an appliance, disable timeouts and return the ssh object.
        :return: paramiko ssh object
        """
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(self.system, **self.connect_args)
        except paramiko.SSHException:
            self.logger.exception("Failed to connect to {}".format(self.system))
            raise
        _, out, _ = ssh.exec_command("unset TMOUT")
        rc = out.channel.recv_exit_status()
        if rc != 0:
            raise RuntimeError("Return code of 'unset TMOUT was {}.".format(rc))
        self.ssh_client = ssh

        # Close this connection after execution
        atexit.register(self.disconnect)

    def disconnect(self):
        try:
            self.ssh_client.close()
        except (AttributeError, NameError):
            logging.debug("No ssh client to close.")
        self.ssh_client = None

    def prep_cmd(self, operation, **update_cmds):
        """
        :return: ActCmd object with ssh_command attribute
        """
        prepared_command = self.ActCmd(operation, **update_cmds)
        prepared_command.ssh_command = self.params_to_cli(operation, **update_cmds)
        return prepared_command

    def call(self, command_obj):
        """
        Use when you explicitly want to connect over ssh and send raw ssh commands.

        This houses the functionality unlike rest method because I want to avoid passing around the client to retain
        channels.

        :param command_obj: Instance of ActCmd object
        :return: stdout, stderr, exit status
        """
        if not self.ssh_client:
            self.connect()

        stdin_chan, stdout_chan, stderr_chan = self.ssh_client.exec_command(command_obj.ssh_command)
        stdin_chan.close()

        # Wait for exit_status
        # Alarm is configured in appliance_connection
        signal.alarm(self.call_timeout)
        exit_status = stdout_chan.channel.recv_exit_status()
        signal.alarm(0)

        # get output from channelfiles
        stdout = stdout_chan.readlines()
        stderr = stderr_chan.readlines()
        self.logger.debug('stderr: \n{}'.format(stderr))
        self.logger.debug("exit status: {}".format(exit_status))
        command_obj.stdout = stdout
        command_obj.stderr = stderr
        command_obj.exit_status = exit_status

    def post_cmd(self, command_obj):
        command_obj.result = self.convert_ssh_output(command_obj.stdout, command_obj.stderr)
        return super(ApplianceSsh, self).post_cmd(command_obj)

    @staticmethod
    def strip_newlines(li):
        return [line.strip('\n') for line in li]

    def raw(self, ssh_command):
        c = self.ActCmd()
        c.ssh_command = ssh_command
        self.call(c)
        c.stdout = self.strip_newlines(c.stdout)
        c.stderr = self.strip_newlines(c.stderr)
        return c.stdout, c.stderr, c.exit_status

    def params_to_cli(self, operation, **update_cmds):
        """
        Takes a functional cli operation and appends rest like inputs.

        ex.
          self.cmd('udsinfo lshost', filtervalue='ostype=Linux')
        returns:
          "/act/bin/udsinfo lshost -filtervalue 'ostype=Linux'"
        :param operation: A functional cli operation
        :param update_cmds:
        :return:
        """
        cli_command = operation.partition(' ')[0]
        if 'udsinfo' in cli_command:
            cli_command = '/act/bin/udsinfo'
        elif 'udstask' in cli_command:
            cli_command = '/act/bin/udstask'
        elif 'sainfo' in cli_command:
            cli_command = '/act/bin/sainfo'
        else:
            raise ValueError("Actifio appliance doesn't support command {}, accepted values "
                             "(udsinfo, udstask, sainfo)".format(cli_command))
        body = operation.partition(' ')[2]

        # add parameters to body
        for k, v in update_cmds.items():
            # don't pass None params
            if v is not None:
                parameter = "-{}".format(k)
                # TODO: standardize actual string true responses from Rest switch true
                # handle parameterless switches
                if v == 'true':
                    value = ''
                else:
                    value = " '{}'".format(v)
                option = "{}{}".format(parameter, value)
                body += ' {}'.format(option)
        if 'udsinfo' in cli_command and body.startswith(('ls', 'list')):
            body += " -delim '{}'".format(self.SSH_DELIM)
        full_operation = "{} {}".format(cli_command, body)
        return full_operation

    def convert_ssh_output(self, stdout, stderr):
        self.logger.debug('Parsing stdout: {}'.format(stdout))
        rest_like_result = {}
        # First format stderr
        if stderr:
            error_code = re.match("(?:ACTERR-)(\d+)", stderr[0]).group(1)
            error_message = re.match("(?:ACTERR-\d+ )(.+)", stderr[0]).group(1)
            rest_like_result['errorcode'] = error_code
            rest_like_result['errormessage'] = error_message
        # Now format stdout
        try:
            # Handle udsinfo commands that start with ls
            if self.SSH_DELIM in stdout[0]:
                self.logger.info('Ssh operation contains delim, grabbing header.')
                headers = stdout[0].split(self.SSH_DELIM)
                values = [row.split(self.SSH_DELIM) for row in stdout[1:]]
                # Make the result list like JSON response
                result_list = []
                for row in values:
                    result_list.append(dict(zip(headers, row)))
                rest_like_result['result'] = result_list
            else:
                # Handle all other udsinfo commands
                # only return a list if there is more than one item, else return a string (see exception)
                if stdout[1]:
                    rest_like_result = {'result': stdout}
                # TODO Handle commands that match "udsinfo -h | egrep -v '^\s*ls'"
        except IndexError:
            try:
                # return single item response as a string
                rest_like_result['result'] = stdout[0]
            except IndexError:
                # return "[]" if stdout was empty, matching standard rest response
                rest_like_result['result'] = stdout
        self.logger.debug("Converted cli result: {}".format(rest_like_result))
        return rest_like_result
