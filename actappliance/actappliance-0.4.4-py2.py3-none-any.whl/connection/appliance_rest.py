import requests
import json
import shlex
import atexit
import logging
import time
import signal

from actappliance.models import ActResponse
from actappliance.connections.connection import ApplianceConnection

# suppress warnings from verify=False
from requests.packages.urllib3.exceptions import SecurityWarning
requests.packages.urllib3.disable_warnings(SecurityWarning)
# This is required if we want to support old versions of py2
# from requests.packages.urllib3.exceptions import SNIMissingWarning
# requests.packages.urllib3.disable_warnings(SNIMissingWarning)


class ApplianceRest(ApplianceConnection):

    def __init__(self, system, params, call_timeout=6 * 60 * 60):
        """
        :param system: Appliance to connect to (ip or dns name)
        :param params: Dictionary of params to send to connect; ex. {'name': 'ex', 'password': 'ex', 'vendorkey': 'ex'}
        :param call_timeout: Maximum time to spend attempting an individual call
        """
        super(ApplianceRest, self).__init__()
        self.logger = logging.getLogger(__name__)

        self.system = system
        self.call_timeout = call_timeout
        self.params = params if params is not None else {}

        # Set in method 'connect'
        self.s = self.sid = None

    def connect(self):
        """Connect and get a sessionid from the appliance."""
        # Ensure we have everything we need to connect before attempting
        for input_ in ['name', 'password', 'vendorkey']:
            if input_ not in self.params:
                raise ValueError("Missing parameter {}, cannot login without it.".format(input_))

        self.s = requests.Session()

        self.logger.info("Logging in as user {}.".format(self.params.get('name', '<no name found>')))

        result = self.s.post("https://" + self.system + "/actifio/api/login", verify=False, params=self.params)
        result.raise_for_status()
        if 'errorcode' in result.json():
            raise ValueError("Failed to connect: {}".format(result.json()))

        self.sid = result.json()['sessionid']
        self.logger.info('Sessionid {} acquired.'.format(self.sid))

        self.s.keep_alive = False

        # Sign out after execution
        atexit.register(self.disconnect, sid=self.sid)

    def disconnect(self, sid=None):
        """Logout of an actifio rest session."""
        if sid is None:
            sid = self.sid

        # Only try to disconnect if we have a sid. It takes a long time to retry connection to a non-existent machine.
        if sid:
            self.logger.debug("Logging out of session {}".format(sid))
            url = ("https://{}/actifio/api/logout?sessionid={}".format(self.system, sid))
            try:
                self.s.post(url, verify=False)
            except requests.ConnectionError:
                # Don't raise connection error. It's safe to let it timeout.
                logging.warning("Unable to logout of session, it may have already expired.")
            self.s.close()

        # set sid to None for the case where it was set as self.sid
        sid = None

    def prep_cmd(self, command, **update_cmds):
        if not self.sid:
            self.connect()

        command = self.ActCmd(command, **update_cmds)
        command.method, command.url, command.params = self.cli_to_rest(command.operation)
        command.params.update(update_cmds)
        self.logger.debug('Parameters for rest call are {}'.format(command.params))
        return command

    def call(self, command_obj):
        # Alarm is configured in appliance_connection
        signal.alarm(self.call_timeout)
        r = self._protect_sid(command_obj.method, command_obj.url, command_obj.params)
        signal.alarm(0)

        try:
            r.raise_for_status()
        except requests.HTTPError as e:  # NOQA: keep this object for debugging
            self.logger.debug("Bad HTTP Status {}.\nResponse: {}\nUrl {}".format(r.status_code, r.json(), r.url))
            # Let the user handle errors
        command_obj.result = r.json()

    def _protect_sid(self, method, url, params, verify=False, **kwargs):
        """Resend the operation if it looks like the sessionid has been dropped (default times out at 30 minutes)."""
        try:
            r = self.s.request(method, url, params=params, verify=verify, **kwargs)
            self.logger.info('Request url: {}'.format(r.url))
            self.logger.debug(r.content)
            r.raise_for_status()
        except requests.HTTPError as e:
            # errorcode 10020 is User is not logged in
            # {'errorcode': 10020, 'errormessage': 'User is not logged in'}
            try:
                errorcode = r.json()['errorcode']
            except KeyError:
                print(r.json())
                logging.exception("Status code was bad, but no errorcode could be found!")
                raise
            if e.response.status_code == 500 and errorcode == 10020:
                self.logger.exception('Looks like the sessionid expired, re-authenticating and sending again.')
                self.logger.debug(r.json())
                self.logger.debug('Failed command sessionid is {}'.format(self.sid))
                self.connect()
                params['sessionid'] = self.sid
                self.logger.debug('New sessionid is {}'.format(self.sid))
                r = self.s.request(method, url, params=params, verify=verify, **kwargs)

            if e.response.status_code == 500 and errorcode == 10023:
                self.logger.exception('Looks like the server timed out sending again.')
                # TODO: restructure with call class so that reauthentication can be handled at the same time.
                time.sleep(1)
                r = self.s.request(method, url, params=params, verify=verify, **kwargs)

            # Don't re-raise let the user handle all other errors

        return r

    def ui_call(self, method, url_suffix, params=None, data=None, **kwargs):
        """
        Used to send Actifio desktop rest calls.

        :param method: type of rest call to make. ie. GET, POST
        :param input_dictionary: python object to be converted to json
        :param url_suffix: What follows actifio in the UI call. i.e. https://<some_hostname>/actifio/<url_suffix here>
        :return: ActResponse object of request
        """
        if not self.sid:
            self.connect()

        if params is None:
            params = {}
        url = "https://{}/actifio/{}".format(self.system, url_suffix)
        params['sessionid'] = self.sid
        r = self._protect_sid(method, url, params=params, data=data, **kwargs)
        r.raise_for_status()
        # strip the unparseable parts of the response that the UI framework needs and convert to dictionary
        # answer = ast.literal_eval(r.text[1:-1])
        answer = json.loads(r.text[1:-1])
        logging.debug(answer)
        if answer.get('status') != 'ok':
            ar = ActResponse(answer)
            ar.raise_for_error()
        return answer

    def cli_to_rest(self, operation):
        """
        Turn a cli command into rest method, url, and params. Argument should be the first parameter.

        Method and url return are strings while params is a dictionary.
        Argument should be the first command because barring documenting and updating all valueless keynames (i.e.
        -force -nowait etc.) this encoder cannot figure out what parameters are switches and which expect a value.
        :param operation: The full operation to be converted. ex. "udsinfo lshost 1234 -filtervalue some=thing&also=this
        :return: method (str), url (str), params (dict)
        """
        # derive method and call-type from first word
        self.logger.info('Converting cli command "{0}" to rest.'.format(operation))
        command = operation.partition(' ')[0]
        if command == "udsinfo":
            method = 'get'
            call = 'info'
        elif command == "udstask":
            method = 'post'
            call = 'task'
        elif command == "sainfo":
            method = 'get'
            call = 'shinfo'
        else:
            raise ValueError("Actifio appliance doesn't support operation {}, accepted values "
                             "(udsinfo, udstask, sainfo)".format(command))

        # separate action (ex. "lsbackup") and params (ex. "1234 -force -filtervalue key=value") from body
        body = operation.partition(' ')[2]
        split_body = shlex.split(body)
        try:
            action = split_body[0]
        except IndexError as e:
            raise IndexError('Operation provided to convert to cli has no action. ex. "mkhost". {}'.format(e))
        chaos_params = split_body[1:]

        # create param dictionary
        params = {}
        k = None
        v = None
        for i in reversed(chaos_params):
            if i.startswith('-'):
                k = i[1:]
            else:
                if v is None:
                    v = i
                else:
                    # handle sequential values
                    params['argument'] = v
                    v = i
            if k:
                if v:
                    params[k] = v
                    k = None
                    v = None
                else:
                    params[k] = 'true'
                    k = None
                    # don't raise not implemented here, let appliance tell user input problems
        # grab the argument if it's the first parameter
        if v is not None:
            params['argument'] = v

        if self.sid:
            params['sessionid'] = self.sid
        else:
            self.logger.warning('Warning: No sessionid please append sessionid: <sessionid> to params before sending.')
        # format url
        url = ("https://" + self.system + "/actifio/api/" + call + "/" + action)
        return method, url, params
