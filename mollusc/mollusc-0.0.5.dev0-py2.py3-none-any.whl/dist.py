# -*- coding: utf-8 -*-
import getpass
from mollusc import sh, util


class NoCredentials(Exception):
    pass


class Twine(object):
    DEFAULT_REPO_URL = 'https://pypi.python.org/pypi'

    def __init__(self, repo_url=None, username=None, password=None):
        self.repo_url = repo_url
        self.username = username
        self.password = password

    def register(self, package, options={}):
        self.call('register', package, options)

    def upload(self, dist_files, options={}):
        self.call('upload', dist_files, options)

    def call(self, *args, **kwargs):
        cmd = self.get_command(*args, **kwargs)
        sh.echo(cmd)  # TESTING
        # sh.call(cmd)  # TODO: mask=self.password

    def get_command(self, subcmd, args, options):
        repo_url = self.repo_url or self.DEFAULT_REPO_URL
        username = self.username or getpass.getuser()
        password = self.password

        if not password:
            try:
                import keyring
            except ImportError:
                raise NoCredentials('Password is not provided and keyring is not installed')

            if not keyring.get_password(repo_url, username):
                msg = 'Password for {} {} not found in keyring'.format(repo_url, username)

                if sh.is_interactive():
                    sh.echo(msg)

                    while not password:
                        password = getpass.getpass('Password for {} {}: '.format(repo_url, username))
                else:
                    raise NoCredentials(msg)

        cmd = [
            'twine', subcmd,
            '--repository-url', repo_url,
            '-u', username
        ]

        if password:
            cmd.append('-p')
            cmd.append(self.password)

        for name, value in options.items():
            cmd.append(name)
            cmd.append(value)

        cmd.extend(util.list_not_str(args))
        return cmd
