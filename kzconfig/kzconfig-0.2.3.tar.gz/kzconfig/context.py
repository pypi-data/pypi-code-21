"""
kzconfig.context
~~~~~

Kazoo config library.


"""

from pyrkube import KubeConfigNotFound

from . import kube, meta


class Context(metaclass=meta.Singleton):
    def __init__(self):
        env = kube.api.get('configmap', 'environment').get('data', False)
        couch = kube.api.get('secret', 'couchdb').get('data', False)
        rabbit = kube.api.get('secret', 'rabbitmq').get('data', False)
        master_acct = kube.api.get(
            'secret', 'master-account').get('data', False)
        dns = kube.api.get('secret', 'dns.dnsimple').get('data', False)
