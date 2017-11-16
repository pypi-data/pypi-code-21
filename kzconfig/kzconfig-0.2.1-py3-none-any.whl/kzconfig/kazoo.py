"""
kzconfig.kazoo
~~~~~

Kazoo config library.


"""

import kazoo

from .context import context


master_acct = context.master_acct
env = context.env

# print(master_acct['user'], master_acct['pass'], master_acct['name'], env['uri.crossbar'])

api = kazoo.Client(
    username=master_acct['user'],
    password=master_acct['pass'],
    account_name=master_acct['name'],
    base_url=env['uri.crossbar']
)

api.authenticate()
