import os
import json
from click import ClickException
from vsscli import __version__
from pyvss import manager
from pyvss import __version__ as __pyvss_version__
from pyvss.manager import VssManager, VssError
from base64 import b64decode, b64encode


class VssCLIError(ClickException):
    pass


class CLIManager(VssManager):
    user_agent = 'vsscli/{}+pyvss/{}'.format(__version__,
                                             __pyvss_version__)

    def __init__(self, click, config,
                 offline=False,
                 tk=None,
                 username=None, password=None,
                 debug=False,
                 output=None):
        super(CLIManager, self).__init__(tk)
        self.click = click
        self.output = output
        self.offline = offline
        # debug
        self.debug = debug
        # config dir/file
        self.full_config_path = os.path.expanduser(config)
        # sets username if any
        self.username = username
        # sets password if any
        self.password = password

    @property
    def output_json(self):
        return self.output == 'json'

    def update_endpoints(self, endpoint):
        """ Rebuilds API endpoints
        :param endpoint: Base API endpoint
        :return:
        """
        self.api_endpoint = '{}/v2'.format(endpoint)
        self.base_endpoint = endpoint
        self.token_endpoint = '{}/auth/request-token'.format(endpoint)

    def configure(self, username, password, endpoint):
        self.username = username
        self.password = password
        # update instance endpoints if provided
        self.update_endpoints(endpoint)
        # directory available
        if not os.path.isdir(os.path.dirname(self.full_config_path)):
            os.mkdir(os.path.dirname(self.full_config_path))
        # config file
        if os.path.isfile(self.full_config_path):
            try:
                # load credentials by endpoint
                e_username, e_password, e_api_token = \
                    self.load_profile_from_config(self.base_endpoint)
                if not (e_username and e_password and e_api_token):
                    print('Profile not found.')
                    self.write_config_file()

                if e_username and e_password and e_api_token:
                    confirm = self.click.confirm(
                        'Would you like to replace existing configuration?')
                    if confirm:
                        self.write_config_file()
                else:
                    self.click.echo(
                        'Successfully configured credentials for {}. '
                        'You are ready to use '
                        'VSS CLI.'.format(self.base_endpoint))
            except VssCLIError as ex:
                self.click.echo(ex)
                confirm = self.click.confirm(
                    'Would you like to replace existing configuration?')
                if confirm:
                    self.write_config_file()
        else:
            self.write_config_file()

    def load_profile_from_config(self, endpoint):
        username, password, token = None, None, None
        profiles = self.load_raw_config_file()
        profile = profiles.get(endpoint)
        if profile:
            credentials_decoded = b64decode(profile['auth'])
            token = profile['token']
            username, password = \
                credentials_decoded.split(':')
        return username, password, token

    def load_raw_config_file(self):
        try:
            with open(self.full_config_path, 'r') as f:
                profiles = json.load(f)
                return profiles
        except ValueError as ex:
            raise VssCLIError('Invalid configuration file.')

    def load_config(self):
        try:
            if os.environ.get('VSS_API_ENDPOINT'):
                self.update_endpoints(os.environ.get('VSS_API_ENDPOINT'))
            # check for environment variables
            if os.environ.get('VSS_API_TOKEN') or \
                    (os.environ.get('VSS_API_USER') and
                     os.environ.get('VSS_API_USER_PASS')):
                # don't load config file
                if os.environ.get('VSS_API_TOKEN'):
                    # set api token
                    self.api_token = os.environ.get('VSS_API_TOKEN')
                    return self.username, self.password, self.api_token
                elif os.environ.get('VSS_API_USER') \
                        and os.environ.get('VSS_API_USER_PASS'):
                    # generate a new token - won't save
                    try:
                        self.get_token()
                    except VssError as ex:
                        raise VssCLIError(ex.message)
                    return self.username, self.password, self.api_token
                else:
                    raise VssCLIError(
                        'Environment variables error. Please, verify '
                        'VSS_API_TOKEN or VSS_API_USER and VSS_API_USER_PASS')
            else:
                if self.debug:
                    print('Loading configuration file: {}'.format(
                        self.full_config_path))
                if os.path.isfile(self.full_config_path):
                    # read config and look for profile
                    self.username, self.password, self.api_token = \
                        self.load_profile_from_config(self.base_endpoint)
                    if self.debug:
                        print('Loaded from file {}: {}'.format(
                            self.base_endpoint, self.username
                        ))
                    creds = self.username and self.password
                    if not (creds or self.api_token):
                        raise VssCLIError(
                            "Invalid endpoint {} configuration. \n "
                            "Please, run 'vss configure' to add "
                            "endpoint to "
                            "configuration.".format(self.base_endpoint))
                    try:
                        self.whoami()
                    except VssError as ex:
                        if self.debug:
                            print(ex)
                        self.api_token = self.get_token(self.username,
                                                        self.password)
                        self.write_config_file(new_token=self.api_token)
                    return self.username, self.password, self.api_token
            raise VssCLIError("Invalid configuration. "
                              "Please, run "
                              "'vss configure' to initialize configuration.")
        except Exception as ex:
            raise VssCLIError(str(ex))

    def write_config_file(self, new_token=None):
        """
        Creates or updates configuration file with different
        endpoints.

        :param new_token: new api token to store
        :return:
        """
        token = new_token or self.get_token(self.username,
                                            self.password)
        credentials = u'%s:%s' % (self.username.decode('utf-8'),
                                  self.password.decode('utf-8'))
        config_dict = {self.base_endpoint: {
            'auth': b64encode(credentials.encode('utf8')).strip(),
            'token': token}
        }
        # validate if file exists
        if os.path.isfile(self.full_config_path):
            with open(self.full_config_path, 'r+') as fp:
                _conf_dict = json.load(fp)
                _conf_dict.update(config_dict)
                fp.seek(0)
                json.dump(_conf_dict, fp,
                          sort_keys=True,
                          indent=4,
                          encoding='utf-8')
                fp.truncate()
            self.click.echo('Successfully updated configuration '
                            'file {}'.format(self.full_config_path))
        else:
            with open(self.full_config_path, 'wb') as fp:
                _conf_dict = config_dict
                json.dump(_conf_dict, fp,
                          sort_keys=True,
                          indent=4,
                          encoding='utf-8')
            self.click.echo('Successfully written configuration '
                            'file {}'.format(self.full_config_path))
