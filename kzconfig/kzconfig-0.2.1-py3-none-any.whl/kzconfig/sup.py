"""
kzconfig.sup
~~~~~

Kazoo config library.


"""

import subprocess
from decimal import Decimal

from . import kazoo, kube, util


class KappsMaint:
    module = 'kapps_maintenance'

    @staticmethod
    def refresh(database=''):
        return sup(KappsMaint.module, 'refresh', database)


class KappsAcctConfig:
    module = 'kapps_account_config'

    @staticmethod
    def get(acct, doc, key, default='undefined'):
        if not isinstance(default, str):
            default = str(default)
        return sup(KappsAcctConfig.module, 'get', acct, doc, key, default)

    @staticmethod
    def set(acct, doc, key, value):
        if isinstance(value, bytes):
            value = value.decode()
        return sup(KappsAcctConfig.module, 'set', acct, doc, key, value)

    @staticmethod
    def flush(acct, doc=None, strategy=None):
        args = [acct, doc]
        if strategy:
            args.append(strategy)
        return sup(KappsAcctConfig.module, 'flush', *args)


class KappsConfig:
    module = 'kapps_config'

    @staticmethod
    def get(doc, key, default='undefined', node=None):
        if not isinstance(default, str):
            default = str(default)

        args = [doc, key, default]
        if node:
            args.append(node)
        return sup(KappsConfig.module, 'get', *args)

    @staticmethod
    def set(doc, key, value, node=None):
        if isinstance(value, bytes):
            value = value.decode()

        if isinstance(value, bool):
            func = 'set_boolean'
            value = str(value).lower()
        elif isinstance(value, int):
            func = 'set_integer'
        elif isinstance(value, (float, Decimal)):
            func = 'set_float'
            value = str(value)
        else:
            func = 'set'

        args = [doc, key, value]
        if node:
            args.append(node)
        return sup(KappsConfig.module, func, *args)

    @staticmethod
    def set_json(doc, key, value):
        if not isinstance(value, str):
            value = util.json_dumps(value)

        return sup(KappsConfig.module, 'set_json', doc, key, value)

    @staticmethod
    def set_default(doc, key, value):
        return sup(KappsConfig.module, 'set_default', doc, key, value)

    @staticmethod
    def flush(doc=None, key=None, node=None):
        args = []
        for arg in (doc, key, node):
            if arg:
                args.append(arg)

        return sup(KappsConfig.module, 'flush', *args)


def sup(module, function, *args):
    args = list(args)
    pod = kube.get_pod('kazoo')
    for idx, arg in enumerate(args):
        if isinstance(arg, (int, bool)):
            args[idx] = str(arg)

    args_str = ' '.join([module, function, *args])
    cmd = 'kubectl exec {} -- sup {}'.format(pod, args_str)
    print(cmd)
    return subprocess.getoutput(cmd)


def sup_api(module, function, *args):
    _, result = kazoo.api.sup(module, function, *args)
    return result


def status():
    return sup('kz_nodes', 'status')


# def db_refresh(database=''):
#     return sup('kapps_maintenance', 'refresh', database)


# def acct_flush(acct_id):
#     return sup('kapps_account_config', 'flush', acct_id)


# for backwards compatibility
# def config_set_json(*args, **kwargs):
#     return KappsConfig.set_json(*args, **kwargs)
#
#
# def config_flush(*args, **kwargs):
#     return KappsConfig.flush(*args, **kwargs)
#
#
# def config_set_default(*args, **kwargs):
#     return KappsConfig.set_default(*args, **kwargs)
