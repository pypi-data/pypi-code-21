"""
kzconfig.context
~~~~~

Kazoo config library.


"""

from pyrkube import KubeConfigNotFound

from . import kube, meta


class Context(metaclass=meta.Singleton):
    def __init__(self):
        env = kube.api.get('configmap', 'environment').get('data')
        couch = kube.api.get('secret', 'couchdb').get('data')
        rabbit = kube.api.get('secret', 'rabbitmq').get('data')
        master_acct = kube.api.get(
            'secret', 'master-account').get('data')
        dns = kube.api.get('secret', 'dns.dnsimple').get('data')
