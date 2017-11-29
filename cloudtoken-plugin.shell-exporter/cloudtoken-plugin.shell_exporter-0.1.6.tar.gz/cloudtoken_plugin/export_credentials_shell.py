# Shell exporter for cloudtoken
# Takes assumed credentials as input and writes them out to ~/.config/cloudtoken/tokens.shell which is then read
# by the cloudtoken bash additions which makes them available as environment variables in your shell.
# Input: Credentials
# Output: Credentials written to ~/.config/cloudtoken/tokens.shell

import os
import pwd
import re
import sys
import time
import argparse


class Plugin(object):
    def __init__(self, config):
        self._config = config
        self._name = 'export_credentials_shell'
        self._description = 'Exports credentials to JSON file.'
        self._cloudtoken_filename = "{0}/tokens.shell".format(self._config['config_dir'])
        self._cloudtoken_tmp_filename = "{0}/tokens.tmp".format(self._config['config_dir'])

    def __str__(self):
        return __file__

    @staticmethod
    def arguments(defaults):
        parser = argparse.ArgumentParser()
        parser.add_argument("-t",
                            "--temp",
                            dest="temp",
                            action="store_true",
                            default=defaults.get('temp', False),
                            help="Set tokens in this shell only.")
        parser.add_argument("-e",
                            "--export",
                            dest="export",
                            action="store_true",
                            default=defaults.get('export', False),
                            help="Print the tokens.shell file suitable for eval'ing in a shell script.")

        return parser

    def execute(self, data, args, flags):
        if not os.path.exists(self._config['config_dir']):
            os.mkdir(self._config['config_dir'])

        try:
            credentials = dict(data[-1])['data']
        except KeyError:
            print("Unable to load credential data. Exiting.")
            exit(1)

        envvars_daemon_mode = [('AWS_ACCOUNT_ID', '{AWS_ACCOUNT_ID}'),
                               ('AWS_ROLE_NAME', '{AWS_ROLE_NAME}'),
                               ('AWS_EXPIRATION_TIMESTAMP', '{AWS_EXPIRATION_TIMESTAMP}'),
                               ('AWS_LASTUPDATED', '{AWS_LASTUPDATED}')]

        envvars_standard = [
            ('AWS_ACCESS_KEY_ID', '{AWS_ACCESS_KEY_ID}'),
            ('AWS_SECRET_ACCESS_KEY', '{AWS_SECRET_ACCESS_KEY}'),
            ('AWS_SECURITY_TOKEN', '{AWS_SECURITY_TOKEN}'),
            ('AWS_SESSION_TOKEN', '{AWS_SECURITY_TOKEN}'),
            ('AWS_EXPIRATION', '{AWS_EXPIRATION}'),
            ('AWS_DELEGATION_TOKEN', '{AWS_SECURITY_TOKEN}'),
            ('AWS_EXPIRATION_TIMESTAMP', '{AWS_EXPIRATION_TIMESTAMP}'),
            ('AWS_ACCOUNT_ID', '{AWS_ACCOUNT_ID}'),
            ('AWS_LASTUPDATED', '{AWS_LASTUPDATED}'),
            ('AWS_ROLE_NAME', '{AWS_ROLE_NAME}'),
        ]

        envvars = envvars_daemon_mode if args.daemon else envvars_standard

        shell = os.environ["SHELL"]
        template = '#!{SHELL}\n'

        if shell.endswith('fish'):
            template += '\n'.join(['set -xg ' + p[0] + ' ' + p[1] for p in envvars])
        else:
            template += '\n'.join(['export ' + p[0] + '=' + p[1] for p in envvars])

        aws_role_arn = re.search('arn:aws:iam::([0-9]+):role/([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)', credentials['LastRole'])
        aws_role_name = aws_role_arn.group(2)

        template = template.format(AWS_ACCESS_KEY_ID=credentials["AccessKeyId"],
                                   AWS_SECRET_ACCESS_KEY=credentials["SecretAccessKey"],
                                   AWS_SECURITY_TOKEN=credentials["Token"],
                                   AWS_SESSION_TOKEN=credentials["Token"],
                                   AWS_EXPIRATION=credentials["Expiration"],
                                   AWS_EXPIRATION_TIMESTAMP=credentials["Expiration"],
                                   AWS_ACCOUNT_ID=credentials['AccountId'],
                                   AWS_LASTUPDATED=credentials['LastUpdated'],
                                   AWS_ROLE_NAME=aws_role_name,
                                   SHELL=shell)

        if args.temp:
            # Write out a temp file for local shell token import only
            with open(self._cloudtoken_tmp_filename, "w") as fh:
                fh.write(template)
                fh.close()
        else:
            with open(self._cloudtoken_filename, 'w') as fh:
                fh.write(template)
                os.chmod(self._cloudtoken_filename, 0o600)

            # Files get written out as root when in daemon mode so this fixes that.
            if args.daemon:
                if os.path.isfile(self._cloudtoken_filename):
                    user = pwd.getpwnam(args.username)
                    os.chown(self._cloudtoken_filename, user.pw_uid, user.pw_gid)

        data.append({'plugin': self._name, 'data': credentials})

        if args.export:
            self.export()
            exit(0)

        return data

    def unset(self, args):
        if os.path.isfile(self._cloudtoken_filename):
            os.remove(self._cloudtoken_filename)

    @staticmethod
    def export():
        """
        Print the tokens to STDOUT. We define cloudtoken_dir and tokens_shell here because as this method is called
        without having the object instantiated.
        :return: None
        """
        cloudtoken_dir = "{0}/.config/cloudtoken".format(os.path.expanduser('~'))
        tokens_shell = "{0}/tokens.shell".format(cloudtoken_dir)
        if os.path.isfile(tokens_shell):
            now = time.time()
            one_hour_ago = now - 60 * 60  # Number of seconds in one hour
            file_modification = os.path.getmtime(tokens_shell)
            if file_modification < one_hour_ago:
                print("File is more than 60-seconds old.")
                os.remove(tokens_shell)

        if os.path.isfile(tokens_shell):
            file_contents = ''
            with open(tokens_shell, 'r') as f:
                for line in f:
                    if not line.startswith("#"):
                        sys.stdout.write(line)
            f.close()
            print(file_contents)
