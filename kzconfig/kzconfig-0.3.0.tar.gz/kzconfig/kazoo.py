"""
kzconfig.kazoo
~~~~~

Kazoo config library.


"""

import requests
import kazoo


class Kazoo:
    def __init__(self, context):
        self.context = context
        try:
            master_acct = self.context.secrets['master-account']
            env = self.context.configs['environment']
            self.api = kazoo.Client(
                username=master_acct['user'],
                password=master_acct['pass'],
                account_name=master_acct['name'],
                base_url=env['uri.crossbar']
            )
            try:
                self.api.authenticate()
            except requests.ConnectionError:
                pass
        except AttributeError:
            pass
