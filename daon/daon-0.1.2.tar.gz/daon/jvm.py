import os
import time
import atexit

from py4j.java_gateway import (JavaGateway, launch_gateway, GatewayParameters)

install_path = os.path.dirname(os.path.realpath(__file__))

gateway = None


class JvmError(Exception):
  def __init__(self, value):
    self.value = value

  def __str__(self):
    return repr(self.value)


def shutdown_jvm():
  global gateway

  if gateway != None:
    gateway.shutdown()


def init_jvm():
  global gateway

  """Initializes the Java virtual machine (JVM).
  """
  if gateway != None:
    return

  folder_suffix = [
    u'{0}{1}daonCore.jar'
  ]

  javadir = u'%s%sjava' % (install_path, os.sep)
  args = [javadir, os.sep]
  classpath = os.pathsep.join(f.format(*args) for f in folder_suffix)

  port = launch_gateway(classpath=classpath, javaopts=['-Dfile.encoding=UTF8', '-ea', '-Xmx768m'])

  time.sleep(1)
  jvm_e = None
  for i in range(0, 10):
    try:
      time.sleep(1)
      gateway = JavaGateway(gateway_parameters=GatewayParameters(port=port))
    except Exception as e:
      gateway = None
      jvm_e = e
      continue
    break

  if gateway is None:
    if jvm_e:
      raise jvm_e
    raise JvmError("Could not connect to JVM. unknown error")

  atexit.register(shutdown_jvm)


def get_jvm():
  global gateway
  if gateway:
    return gateway.jvm

  return None
