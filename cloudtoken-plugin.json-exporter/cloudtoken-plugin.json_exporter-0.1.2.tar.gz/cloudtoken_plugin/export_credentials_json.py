# JSON exporter for cloudtoken
# Takes assumed credentials as input and writes them out to ~/.config/cloudtoken/tokens.json which is then read
# by various cloudtoken integrations such as the metadata proxy.
# Input: Credentials
# Output: Credentials written to ~/.config/cloudtoken/tokens.json

import os
import pwd
import json
import argparse


class Plugin(object):
    def __init__(self, config):
        self._config = config
        self._name = 'export_credentials_json'
        self._description = 'Exports credentials to JSON file.'

    def __str__(self):
        return __file__

    @staticmethod
    def unset(args):
        if os.path.isfile(args.json_tokens):
            os.remove(args.json_tokens)

    def arguments(self, defaults):
        parser = argparse.ArgumentParser()
        parser.add_argument("-j",
                            "--json-tokens",
                            type=str,
                            dest="json_tokens",
                            help="Specify location of tokens.json file that will be written out.",
                            default=defaults.get('json-tokens', "{0}/tokens.json".format(self._config['config_dir'])))
        parser.add_argument("-t",
                            "--temp",
                            dest="temp",
                            action="store_true",
                            default=defaults.get('temp', False),
                            help="Set tokens in current shell only.")
        return parser

    def execute(self, data, args, flags):
        try:
            credentials = dict(data[-1])['data']
        except KeyError:
            raise Exception("Unable to load credential data. Exiting.")

        if args.temp is False:
            self.write_json(credentials, args)

        data.append({'plugin': self._name, 'data': credentials})
        return data

    @staticmethod
    def write_json(credentials, args):
        with open(args.json_tokens, 'w') as fh:
            fh.write(json.dumps(credentials))
            os.chmod(args.json_tokens, 0o600)

        # Files get written out as root when in daemon mode so this fixes that.
        if args.daemon:
            user = pwd.getpwnam(args.username)
            os.chown(args.json_tokens, user.pw_uid, user.pw_gid)
