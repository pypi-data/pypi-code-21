# -*- coding: utf-8 -*-

"""

mlpods.funpod
~~~~~~~~~~~~~~~~
Functional container

server(docker) usage:
    build a docker image using funpod.handle or funpod.handle_file
    see https://github.com/jcc-ne/mlpods for reference

client(local) usage:
    >>> from mlpods import funpod
    >>> pod = funpod('funpod_rosbad')
    >>> pod.spinup()
    >>> pod.connector.send(...)
"""
from .funpod import FunPodConnector, FunPod
