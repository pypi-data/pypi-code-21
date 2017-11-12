#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import re
import jwt
import pwd
import sys
import logging
import argparse
import requests
import configparser
from shutil import copyfile
from logging.handlers import SysLogHandler


class Akeyra:

    def __init__(self):
        """Setting logging informations"""
        logger = logging.getLogger('akeyra')
        logger.setLevel(logging.INFO)
        filelog = logging.FileHandler('./akeyra.log')
        formatfile = logging.Formatter(
            '[Akeyra][%(asctime)s][%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S')
        filelog.setFormatter(formatfile)
        logger.addHandler(filelog)
        formatsys = logging.Formatter('[Akeyra][%(levelname)s] %(message)s')
        syslog = SysLogHandler(address='/dev/log')
        syslog.setFormatter(formatsys)
        logger.addHandler(syslog)
        """Setting users list"""
        self.userlist = list()
        for item in pwd.getpwall():
            self.userlist.append(item.pw_name)

    def configuration(self):
        """ Get configfile or args.
        Called by __main__.
        """
        self.logger = logging.getLogger('akeyra.init')

        parser = argparse.ArgumentParser(
            description='''You can provide all informations in CLI,
            use the basic configfile (/etc/akeyra.cfg), or an alternative one.
            If nothing is passed by CLI,
            then the basic configfile will be used.''',
            epilog='''If you need to use a proxy, you either set environment
            variable like http_proxy or use proxy in the configfile.'''
        )
        parser.set_defaults(proxy='')
        parser.add_argument("-H", "--host", help="Key Server", metavar="HOST")
        parser.add_argument("-E", "--env", help="Environment", metavar="ENV")
        parser.add_argument("-K", "--key", help="Secret key", metavar="KEY")
        parser.add_argument("-P", "--proxy", help="Proxy", metavar="PROXY")
        parser.add_argument("-F", "--cnf", help="Alt Conffile", metavar="FILE")
        parser.add_argument("-D", "--dry", help="Dry run", action='store_true')

        options = parser.parse_args()

        if (
            options.host is not None and
            options.env is not None and
            options.key is not None
        ):
            if options.proxy is None:
                options.proxy = ""
            self.config = {
                'host': options.host,
                'env': options.env,
                'key': options.key,
                'proxy': options.proxy,
                'dry': options.dry}
        elif options.cnf is not None:
            tcnf = configparser.ConfigParser()
            tcnf.read(options.cnf)
            self.config = {
                'host': tcnf.get('agent', 'host'),
                'env': tcnf.get('agent', 'environment'),
                'key': tcnf.get('agent', 'key'),
                'proxy': tcnf.get('agent', 'proxy', fallback=''),
                'dry': False}
        elif os.path.isfile('/etc/akeyra.cfg'):
            tcnf = configparser.ConfigParser()
            tcnf.read('/etc/akeyra.cfg')
            self.config = {
                'host': tcnf.get('agent', 'host'),
                'env': tcnf.get('agent', 'environment'),
                'key': tcnf.get('agent', 'key'),
                'proxy': tcnf.get('agent', 'proxy', fallback=''),
                'dry': False}
        else:
            self.logger.error("There is no configuration nor configfile.")
            return False

        """This part check if the URI provided is ending with the mandatory
        '/api/' to exploit the Sakeyra app."""
        if re.search(r'/$', self.config['host'], re.I) is None:
            self.config['host'] = '{host}/'.format(host=self.config['host'])
        if re.search(r'/api/$', self.config['host'], re.I) is None:
            self.config['host'] = '{host}api/'.format(host=self.config['host'])

        self.logger.info("Config is : {conf}".format(conf=self.config))
        return True

    def checkurl(self, config):
        """ Check if host exist and is online,
            and get the data from it.
            Called by __main__.
        """
        self.logger = logging.getLogger('akeyra.checkurl')
        checkhost = config['host'] + config['env']
        proxies = {'http': config['proxy'], 'https': config['proxy']}
        request = requests.get(checkhost, proxies)
        if request.status_code == 200:
            self.logger.info(
                "Connection to {host} is OK".format(host=checkhost))
            status = True
            self.data = jwt.decode(
                request.text, config['key'], algorithms=['HS256'])
        else:
            self.logger.error(
                "Connection to {host} is KO".format(host=checkhost))
        return status

    def checkusers(self, user):
        """ Check if user exists
            if user doesn't exist it create user with no password.
            Called by majkeys
        """
        self.logger = logging.getLogger('akeyra.checkusers')
        if user in self.userlist:
            self.logger.info('User {user} exist.'.format(user=user))
            return user
        else:
            os.system('useradd -m  {user}'.format(user=user))
            os.system('mkdir /home/{user}/.ssh/'.format(user=user))
            self.logger.info('User {user} created.'.format(user=user))
            return user

    def copykeys(self, user):
        """ Copy authorized_keys file to user's home
            Add permissions to the file.
            Called by majkeys
        """
        self.logger = logging.getLogger('akeyra.copykeys')
        tfile = '/tmp/{user}'.format(user=user)
        if user == 'root':
            path = '/root/.ssh'
        else:
            path = '/home/{user}/.ssh'.format(user=user)
        authfile = '{path}/authorized_keys'.format(path=path)
        copyfile(tfile, authfile)
        os.system('chown {user}:{user} -R {path}'.format(user=user, path=path))
        os.system('chmod 0600 {path}/*'.format(path=path))
        self.logger.info('Keys for {user} updated'.format(user=user))

    def majkeys(self):
        """ Create the authorized_keys file to /tmp
            Call copykeys(), then remove the file from /tmp
        """
        self.logger = logging.getLogger('akeyra.majkeys')
        self.userset = set()
        bundle = self.data['users']
        for user in bundle:
            for key, value in user.items():
                self.userset.add(key)
                tfile = open("/tmp/{user}".format(user=key), "a")
                authkey = '{key} {email}'.format(
                    key=value["pubkey"],
                    email=value["email"])
                tfile.write('{line}\n'.format(line=authkey))
                tfile.close()
        if self.config['dry'] is False:
            for user in self.userset:
                self.checkusers(user)
                self.copykeys(user)
                self.logger.info(
                    'Removing temp file for {user}'.format(user=user))
                os.remove('/tmp/{user}'.format(user=user))
        else:
            self.logger.warning("Dry run")
            for user in self.userset:
                print('{user} has keys'.format(user=user))
                self.logger.warning('{user} has keys'.format(user=user))
                os.remove('/tmp/{user}'.format(user=user))


def main():
    client = Akeyra()
    if client.configuration() and client.checkurl(client.config):
        client.majkeys()
    else:
        sys.exit()


if __name__ == '__main__':
    main()
