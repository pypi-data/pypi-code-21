"""
kzconfig.kube
~~~~~

Kazoo config library.


"""

import pyrkube


try:
    api = pyrkube.KubeAPIClient()
except KubeConfigNotFound:
    api = False


def get_pod(name):
    pods = api.get('pod', selector=dict(app=name))
    if pods:
        pod = pods[0]
        return pod.name
