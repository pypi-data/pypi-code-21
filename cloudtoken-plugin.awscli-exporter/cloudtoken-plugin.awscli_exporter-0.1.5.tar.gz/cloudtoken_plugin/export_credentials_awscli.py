# AWS CLI export plugin for cloudtoken.
# Writes the assumed credentials to the ~/.aws/credentials file under a profile which equals the role name
# You can then run aws --profile <role> to use those credentials.
# Input: Credentials
# Output: Credentials written to ~/.aws/credentials

import os
import re
import configparser
import collections
import argparse


class Plugin(object):
    def __init__(self, config):
        self._config = config
        self._name = 'export_credentials_cli'
        self._description = 'Exports credentials AWS CLI credentials file..'

    def __str__(self):
        return __file__

    @staticmethod
    def unset(args):
        pass

    @staticmethod
    def arguments(defaults):
        parser = argparse.ArgumentParser()
        return parser

    def execute(self, data, args, flags):
        try:
            credentials = dict(data[-1])['data']
        except KeyError:
            raise Exception("Unable to load credential data. Exiting.")

        awscli_dir = "{0}/.aws".format(os.path.expanduser('~'))
        awscli_credentials_filename = "{0}/credentials".format(awscli_dir)

        aws_role_arn = re.search('arn:aws:iam::([0-9]+):role/([A-Za-z0-9]+(?:-[A-Za-z0-9]+)*)', credentials['LastRole'])
        aws_role_name = aws_role_arn.group(2)

        config = configparser.ConfigParser()

        config.read(awscli_credentials_filename)

        aws_cli_data = {
            'aws_access_key_id': credentials["AccessKeyId"],
            'aws_secret_access_key': credentials["SecretAccessKey"],
            'region': 'us-east-1',
            'aws_session_token': credentials["Token"],
        }
        config[aws_role_name] = collections.OrderedDict(sorted(aws_cli_data.items(), key=lambda t: t[0]))

        with open(awscli_credentials_filename, 'w') as fh:
            config.write(fh)
            os.chmod(awscli_credentials_filename, 0o600)

        data.append({'plugin': self._name, 'data': credentials})
        return data
