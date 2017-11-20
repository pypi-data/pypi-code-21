"""
kzconfig.kazoo
~~~~~

Kazoo config library.


"""

import kazoo

from .context import Context


context = Context()

try:
    master_acct = context.master_acct
    env = context.env
    api = kazoo.Client(
        username=master_acct['user'],
        password=master_acct['pass'],
        account_name=master_acct['name'],
        base_url=env['uri.crossbar']
    )
    api.authenticate()
except AttributeError:
    api = False
