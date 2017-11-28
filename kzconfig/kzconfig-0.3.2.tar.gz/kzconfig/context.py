"""
kzconfig.context
~~~~~

Kazoo config library.

"""
from urllib.parse import urlparse, unquote

import pyrkube

from . import meta, util
from .dns import DNS
from .couch import CouchDB
from .kazoo import Kazoo
from .sup import Sup
from .kubectl import KubeCtl
from .kube import Kube


class Context(metaclass=meta.Singleton):
    _configs = ('environment',)
    _secrets = ('couchdb', 'rabbitmq', 'master-account', 'dns.dnsimple')

    def __init__(self, domain='telephone.org'):
        self.domain = domain

    def _get_configmap(self, name):
        return self.kube.api.get('configmap', name).data

    def _get_secret(self, name):
        return self.kube.api.get('secret', name).data

    @meta.lazy_property
    def configs(self):
        try:
            return {cm: self._get_configmap(cm) for cm in self._configs}
        except AttributeError:
            pass

    @meta.lazy_property
    def secrets(self):
        try:
            return {s: self._get_secret(s) for s in self._secrets}
        except AttributeError:
            pass

    @meta.lazy_property
    def kube(self):
        return Kube(self)

    @meta.lazy_property
    def couchdb(self):
        return CouchDB(self)

    @meta.lazy_property
    def kazoo(self):
        return Kazoo(self)

    @meta.lazy_property
    def dns(self):
        return DNS(self)

    @meta.lazy_property
    def sup(self):
        return Sup(self)

    @meta.lazy_property
    def kubectl(self):
        return KubeCtl(self)
