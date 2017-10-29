# coding: utf-8
"""
    bluelens-spawning-pool

    Contact: master@bluehack.net
"""

from __future__ import absolute_import

import redis

REDIS_SERVER = 'bl-mem-store'


class SpawningPool(object):
  def __init__(self):
    self._metadata_labels = {}
    self._containers = []
    self._rconn = redis.StrictRedis(REDIS_SERVER, port=6379)

  def setApiVersion(self, version):
    self._api_version = version

  def setKind(self, kind):
    self._kind = kind

  def setMetadataName(self, name):
    self._metadata_name = name

  def setMetadataNamespace(self, namespace):
    self._metadata_namespace = namespace

  def addMetadataLabel(self, key, value):
    self._metadata_labels[key] = value

  def createContainer(self):
    container = {}
    container['env'] = []
    return container

  def addContainer(self, container):
    self._containers.append(container)

  def setContainerName(self, container, name):
    container['name'] = name

  def addContainerEnv(self, container, key, value):
    env = {}
    env[key] = value
    container['env'].append(env)

  def setContainerName(self, container, name):
    container['name'] = name

  def setContainerImage(self, container, image):
    container['image'] = image

  def setRestartPolicy(self, policy):
    self._restart_policy = policy

  def spawn(self):
    config = {}

    config['apiVersion'] = self._api_version
    config['kind'] = self._kind

    metadata = {}
    metadata['name'] = self._metadata_name
    metadata['namespace'] = self._metadata_namespace
    metadata['labels'] = self._metadata_labels
    config['metadata'] = metadata

    spec = {}
    spec['containers'] = self._containers
    spec['restartPolicy'] = self._restart_policy
    config['spec'] = spec

    str_config = self.stringify(config)
    print(str_config)
    self._rconn.publish('spawn/create', str_config)

  def stringify(self, dic):
    return str(dic)



