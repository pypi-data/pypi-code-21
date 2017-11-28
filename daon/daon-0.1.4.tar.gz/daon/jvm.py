import os
import sys, traceback
import atexit

from py4j.java_gateway import (JavaGateway, launch_gateway, GatewayParameters, Py4JNetworkError)

install_path = os.path.dirname(os.path.realpath(__file__))

gateway = None


def shutdown_jvm():
  global gateway

  if gateway != None:
    gateway.shutdown()


def init_jvm():
  global gateway

  """Initializes the Java virtual machine (JVM).
  wrong.. still valid check first
  if fail and not running then recreate
  else reuse it
  """
  if gateway != None:
    if check_valid():
      return
    else:
      shutdown_jvm()

  port = launch()

  gateway = JavaGateway(gateway_parameters=GatewayParameters(port=port))

  atexit.register(shutdown_jvm)


def check_valid():
  global gateway

  try:
    gateway.jvm.System.getProperty("java.runtime.name")
    return True
  except Py4JNetworkError:
    print("No JVM listening. restart gateway...")
    # traceback.print_exc(file=sys.stderr)
    return False
  except Exception:
    print("Another type of problem... maybe with the JVM")
    traceback.print_exc(file=sys.stderr)
    return False


def launch():
  lib_dir = u'%s%sjava%sdaonCore.jar' % (install_path, os.sep, os.sep)
  classpath = os.pathsep.join([lib_dir])
  port = launch_gateway(classpath=classpath, javaopts=['-Dfile.encoding=UTF8', '-ea', '-Xmx768m'])
  return port


def get_jvm():
  global gateway
  if gateway:
    return gateway.jvm

  return None
