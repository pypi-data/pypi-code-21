"""
kzconfig.sup
~~~~~

Kazoo config library.


"""

import subprocess
from decimal import Decimal

from . import util


class SupCommandBase:
    def __init__(self, parent):
        self.parent = parent
        self.sup = parent.sup


class KappsMaint(SupCommandBase):
    module = 'kapps_maintenance'

    def refresh(self, database=''):
        return self.sup(self.module, 'refresh', database)

    def blocking_refresh(self, database=''):
        return self.sup(self.module, 'blocking_refresh', database)


class KappsAcctConfig(SupCommandBase):
    module = 'kapps_account_config'

    def get(self, acct, doc, key, default='undefined'):
        if not isinstance(default, str):
            default = str(default)
        return self.sup(self.module, 'get', acct, doc, key, default)

    def set(self, acct, doc, key, value):
        if isinstance(value, bytes):
            value = value.decode()
        return self.sup(self.module, 'set', acct, doc, key, value)

    def flush(self, acct, doc=None, strategy=None):
        args = [acct, doc]
        if strategy:
            args.append(strategy)
        return self.sup(self.module, 'flush', *args)


class KappsConfig(SupCommandBase):
    module = 'kapps_config'

    def get(self, doc, key, default='undefined', node=None):
        if not isinstance(default, str):
            default = str(default)

        args = [doc, key, default]
        if node:
            args.append(node)
        return self.sup(self.module, 'get', *args)

    def set(self, doc, key, value, node=None):
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
        return self.sup(self.module, func, *args)

    def set_json(self, doc, key, value):
        if not isinstance(value, str):
            value = util.json_dumps(value)

        return self.sup(self.module, 'set_json', doc, key, value)

    def set_default(self, doc, key, value):
        return self.sup(self.module, 'set_default', doc, key, value)

    def flush(self, doc=None, key=None, node=None):
        args = []
        for arg in (doc, key, node):
            if arg:
                args.append(arg)

        return self.sup(self.module, 'flush', *args)


class KazooNodes(SupCommandBase):
    module = 'kz_nodes'
    def status(self):
        return self.sup(self.module, 'status')


class Sup:
    def __init__(self, context):
        self.context = context
        self.kapps_maintenance = KappsMaint(self)
        self.kapps_account_config = KappsAcctConfig(self)
        self.kapps_config = KappsConfig(self)
        self.kz_nodes = KazooNodes(self)

    def sup(self, module, function, *args):
        args = list(args)
        try:
            pod = self.context.kube.api.get_first('pod', selector=dict(app='kazoo'))
        except TypeError:
            raise RuntimeError('No kazoo app pod found')

        for idx, arg in enumerate(args):
            if isinstance(arg, (int, bool)):
                args[idx] = str(arg)

        args_str = ' '.join([module, function, *args])
        cmd = 'kubectl exec {} -- sup {}'.format(pod.name, args_str)
        print(cmd)
        return subprocess.getoutput(cmd)

    def sup_api(self, module, function, *args):
        _, result = self.context.kazoo.sup(module, function, *args)
        return result
