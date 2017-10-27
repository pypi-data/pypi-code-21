"""
    COPYRIGHT (C) 2017 by Sebastian Stigler

    NAME
        server_token.py -- Code to handle tokens

    FIRST RELEASE
        2017-07-20  Sebastian Stigler  sebastian.stigler@hs-aalen.de

"""
import argparse
import configparser
import getpass
import logging
import os.path
import sys

import coloredlogs
import jwt
import requests

from datetime import datetime
from pkg_resources import resource_filename
from urllib.parse import urljoin

from messgeraet_anzapfen import __version__
from messgeraet_anzapfen.serial import hashserial
from messgeraet_anzapfen.verify import verify_sensor_id

_logger = logging.getLogger(__name__)


class Token:
    """handles tokens"""

    template = ('  Hardware ID : {hwid}\n'
                '  Sensor IDs  : {ids}\n'
                '  HTTP Methods: {mtds}\n'
                '  Expires {qual}  : {exp}\n')
    template_token = template + '  Issuer      : {iss}\n'

    def __init__(self, configfilename):
        self.configfilename = configfilename

        config = configparser.ConfigParser(default_section='Token')
        config.read(self.configfilename)
        self.config = config
        self.token = self.config['Token']

    def write(self):
        """write the config back to the given filename"""
        with open(self.configfilename, 'w') as cfgfile:
            self.config.write(cfgfile)
        _logger.debug('Write config to %r', self.configfilename)

    def add_id(self, sensor_id, keep=True):
        """add sensor_id to list of sensors names for the database"""
        if keep and 'Token' in self.config:
            id_list = self.config['Token'].get('ids', '').split(',')
        else:
            id_list = []
        [verify_sensor_id(sensor_id) for sensor_id in id_list]
        if not (isinstance(sensor_id, str) and sensor_id.strip()):
            _logger.warning('sensor_id is a empty string')
            return False
        if sensor_id not in id_list:
            id_list.append(sensor_id.strip())
        _logger.debug('Set ids to %r', id_list)
        self.config.set('Token', 'ids', ','.join(id_list))
        return True

    def add_mtd(self, mtd, keep=True):
        """add mtd to list of sensors names for the database"""
        if keep:
            mtds_list = self.config['Token'].get('mtds', 'POST').split(',')
        else:
            mtds_list = []
        if not (isinstance(mtd, str) and mtd.strip()):
            _logger.warning('mtd is a empty string')
            return False
        if mtd not in mtds_list:
            mtds_list.append(mtd.strip())
        _logger.debug('Set mtds to %r', mtds_list)
        self.config.set('Token', 'mtds', ','.join(mtds_list))
        return True

    def set_exp(self, exp, force=False):
        """set the expire date for the token request"""
        if isinstance(exp, int) and (exp > 0 or force):
            if exp <= 0:
                exp = -1
            else:
                exp *= 24
            self.config.set('Token', 'exp', str(exp))
            _logger.debug('Set exp to %r h', exp)
            return True
        else:
            _logger.warning('exp is not an positiv integer')
            return False

    def check_token(self):
        """returns a string with the decoded entries of the token"""
        response = 'Values of token:\n'
        try:
            data = jwt.decode(self.token.get('token', ''), verify=False)
            if 'exp' in data:
                data['exp'] = str(datetime.fromtimestamp(data['exp']))
                data['qual'] = 'at'
            else:
                data['exp'] = 'never'
                data['qual'] = '  '
            if 'uni' in data:
                if data['uni']:
                    self.template_token += '  Universal   : {uni}\n'
                else:
                    del data['uni']
            response += self.template_token.format(**data)
        except jwt.exceptions.DecodeError:
            response += '  Not set yet.\n'
        return response

    def check_token_request(self):
        """returns a string with the requested entries of a new token"""
        response = 'Values for the token request:\n'
        _exp = self.token.getint('exp', '24')
        if _exp > 0:
            exp = '%.1f Days (%d Hours)' % (_exp/24., _exp)
            qual = 'in'
        else:
            exp = 'never'
            qual = '  '
        id_list = self.config['Token'].get('ids', '').split(',')
        [verify_sensor_id(sensor_id) for sensor_id in id_list]
        response += self.template.format(
                hwid=self.token.get('hwid', hashserial()),
                ids=id_list,
                qual=qual,
                mtds=self.token.get('mtds', 'POST').split(','),
                exp=exp)
        if self.token.get('uni', 'False').lower() == 'true':
            response += '  Universal   : True\n'
        return response

    def get_token_from_server(self, retries=3):
        """sends a tokenrequest to the server"""
        result = False
        data = {
            'hwid': self.token.get('hwid', hashserial()),
            'ids': self.token.get('ids', '').split(','),
            'mtds': self.token.get('mtds', 'POST').split(','),
            'exp': self.token.getint('exp', 24)
            }

        if self.token.get('uni', 'False').lower() == 'true':
            data['uni'] = True

        if '' in data['ids']:
            _logger.warning('No sensor_ids registered')
            return result

        url = None
        if 'Server' in self.config:
            url = self.config['Server'].get('url')
        if url is not None:
            url = urljoin(url, 'token')
        else:
            _logger.warning('No url set in Server section')
            return result

        while not result and retries > 0:
            retries -= 1
            print('Type login credetials for request to', url)
            user = input('  User: ')
            passwd = getpass.getpass('  Password: ')
            auth = (user, passwd)
            try:
                response = requests.post(url, json=data, auth=auth, timeout=10)
                _logger.debug('Response for token request: %s', response.text)
                response.raise_for_status()
                self.config.set('Token', 'token', response.json()['token'])
                result = True
            except requests.exceptions.HTTPError as err:
                _logger.error('{typ}: {err}'.format(
                    typ=err.__class__.__name__, err=err))
                if response.status_code != 403:
                    # Not an authentication error -> stop looping
                    break
            except requests.exceptions.RequestException as err:
                _logger.error('{typ}: {err}'.format(
                    typ=err.__class__.__name__, err=err))
                break
        return result


def parse_args(args):

    parser = argparse.ArgumentParser(
        description="Token manipulation tool")

    parser.add_argument(
        '--version',
        action='version',
        version='messgeraet_anzapfen {ver}'.format(ver=__version__))
    parser.add_argument(
        '-v',
        '--verbose',
        dest="loglevel",
        help="set loglevel to INFO",
        action='store_const',
        const=logging.INFO)
    parser.add_argument(
        '-vv',
        '--very-verbose',
        dest="loglevel",
        help="set loglevel to DEBUG",
        action='store_const',
        const=logging.DEBUG)

    subparsers = parser.add_subparsers(
        title='subcommands',
        description='valid subcommands')

    parser_c = subparsers.add_parser(
        'create',
        description='Create a token from the current settings',
        help=('Requests a token from the server with the current settings in '
              'the token.ini file'))
    parser_c.set_defaults(func=main_create)

    parser_u = subparsers.add_parser(
        'update',
        description='Update the settings for a prospective token',
        help=('Set the parameters for a future token. You must call the '
              '\'create\' subcommand to request the actual token!'))
    group_u = parser_u.add_mutually_exclusive_group(required=True)
    group_u.add_argument(
        '-s',
        '--sensor_id',
        dest='sensor_id',
        nargs='*',
        help=('Space separated list of all sensor_ids which the token will be '
              'resposible for.'))
    group_u.add_argument(
        '-S',
        '--sensor_id_from_ini_files',
        dest='sensor_id_from_ini_files',
        nargs='*',
        help=('Space separated list of \'anzapfen\' ini files from which the '
              'sensor_id will be extracted.'))
    group_u.add_argument(
        '-e',
        '--expires_in',
        dest='expires_in',
        type=int,
        help='The number of days (> 0) the token will be valid.')
    group_u.add_argument(
        '-n',
        '--not-expire',
        dest='not_expire',
        action='store_true',
        help=('Force to token to not expire. You need special permission on '
              'the server to request such a token!'))
    group_u.add_argument(
        '-m',
        '--methods',
        dest='methods',
        nargs='*',
        choices=['DELETE', 'GET', 'PATCH', 'POST', 'PUT'],
        help=('Space separated list of HTTP methods, which will be allowed by '
              'the token.'))
    parser_u.add_argument(
        '-k',
        '--keep',
        dest='keep',
        action='store_true',
        help=('Keep the current value in the \'token.ini\' file and append '
              'the new ones.'))
    parser_u.set_defaults(func=main_update)

    parser_s = subparsers.add_parser(
        'show',
        description='Show the values of the request and the current token',
        help=('Prints the values which are sent to request a new token and'
              'show the stored values in the current token'))
    parser_s.set_defaults(func=main_show)

    ret = parser.parse_args(args)
    if 'func' not in ret:
        parser.print_help()
        sys.exit(0)
    return ret


def main_create(args):
    """Main for create subcommand"""

    token = Token('token.ini')
    print(token.check_token_request())
    if token.get_token_from_server():
        token.write()
        print()
        print(token.check_token())


def main_update(args):
    """Main for create subcommand"""

    token = Token('token.ini')
    if 'sensor_id' in args and args.sensor_id:
        keep = args.keep
        for entry in args.sensor_id:
            if not token.add_id(entry, keep):
                break
            keep = True
        else:
            token.write()

    if 'sensor_id_from_ini_files' in args and args.sensor_id_from_ini_files:
        keep = args.keep
        for entry in args.sensor_id_from_ini_files:
            cfg = configparser.ConfigParser()
            cfg.read(entry)
            sensor_id = cfg['DEFAULT'].get('sensor_id', '')
            if not token.add_id(sensor_id, keep):
                break
            keep = True
        else:
            token.write()

    if 'methods' in args and args.methods:
        keep = args.keep
        for entry in args.methods:
            if not token.add_mtd(entry, keep):
                break
            keep = True
        else:
            token.write()

    if 'expires_in' in args and args.expires_in is not None:
        if token.set_exp(args.expires_in):
            token.write()

    if 'not_expire' in args and args.not_expire:
        if token.set_exp(-1, True):
            token.write()

    print(token.check_token_request())


def main_show(args):
    """Main for create subcommand"""

    token = Token('token.ini')
    print('Requesting a token from \n  %s\n' %
          token.config['Server'].get('url'))
    print(token.check_token_request())
    print(token.check_token())


def run():
    """Entry point for console_scripts
    """
    if not os.path.exists('token.ini'):
        tokentemplate = resource_filename('messgeraet_anzapfen', 'token.ini')
        with open(tokentemplate) as tempfile:
            with open('token.ini', 'w') as tokenfile:
                tokenfile.write(tempfile.read())

    args = parse_args(sys.argv[1:])
    logformat = "%(message)s"
    logformat = "[%(asctime)s] %(message)s"
    coloredlogs.install(
        fmt=logformat,
        datefmt="%Y-%m-%d %H:%M:%S",
        level=args.loglevel)
    try:
        args.func(args)
    except ValueError as err:
        _logger.error('Value Error: %s' % err)
    except KeyboardInterrupt:
        _logger.warning('Aborted by user')

if __name__ == '__main__':
    run()
# vim: ft=python ts=4 sta sw=4 et ai
# python: 3
