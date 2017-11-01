"""
kzconfig.context
~~~~~

Kazoo config library.


"""

from . import kube


class context:
    env = kube.api.get('configmap', 'environment').data
    couch = kube.api.get('secret', 'couchdb').data
    master_acct = kube.api.get('secret', 'master-account').data
