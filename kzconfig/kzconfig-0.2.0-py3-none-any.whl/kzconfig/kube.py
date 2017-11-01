"""
kzconfig.kube
~~~~~

Kazoo config library.


"""

import pyrkube


api = pyrkube.KubeAPIClient()


def get_pod(name):
    pods = api.get('pod', selector=dict(app=name))
    if pods:
        pod = pods[0]
        return pod.name
