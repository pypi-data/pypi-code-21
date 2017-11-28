"""
kzconfig.kubectl
~~~~~

Kazoo config library.


"""

class KubeCtlCommandBase:
    def __init__(self, context):
        self.context = context

    def _build_command(self, *args):
        args = ['kubectl', self.command] + list(args)
        return ' '.join(args)


class KubeCtlConfig(KubeCtlCommandBase):
    command = 'config'

    def set_credentials(self, name='admin', token=''):
        args = ['set-credentials', name]
        if token:
            args.append('--token={}'.format(token))
        return self._build_command(*args)

    def set_context(self, name='local', cluster='local', user='admin',
                    namespace=''):
        args = ['set-context', name]
        kwargs = dict(cluster=cluster, user=user, namespace=namespace)
        for k, v in kwargs.items():
            args.append('--{}={}'.format(k, v))
        return self._build_command(*args)


class KubeCtl:
    def __init__(self, context):
        self.context = context
        self.config = KubeCtlConfig(self)
