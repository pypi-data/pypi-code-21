"""
kzconfig.sup
~~~~~

Kazoo config library.


"""

import subprocess

from . import kazoo, kube, util


def sup(module, function, *args):
    pod = kube.get_pod('kazoo')
    args_str = ' '.join([module, function, *args])
    cmd = 'kubectl exec {} -- sup {}'.format(pod, args_str)
    return subprocess.getoutput(cmd)


def sup_api(module, function, *args):
    _, result = kazoo.api.sup(module, function, *args)
    return result


def status():
    return sup('kz_nodes', 'status')


def db_refresh(database=''):
    return sup('kapps_maintenance', 'refresh', database)


def config_set_json(doc, key, value):
    if not isinstance(value, str):
        value = util.json_dumps(value)

    return sup('kapps_config', 'set_json', doc, key, value)


def config_flush(doc=None, key=None, node=None):
    args = []
    if doc:
        args.append(doc)
    if key:
        args.append(key)
    if node:
        args.append(node)

    return sup('kapps_config', 'flush', *args)


def config_set_default(doc, key, value):
    return sup('kapps_config', 'set_default', doc, key, value)


def acct_flush(acct_id):
    return sup('kapps_account_config', 'flush', acct_id)
