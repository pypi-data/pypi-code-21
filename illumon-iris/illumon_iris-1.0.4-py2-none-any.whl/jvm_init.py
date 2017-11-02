#
# Copyright (c) 2016-2017 Illumon and Patent Pending
#

import logging
import os
import os.path
from glob import glob
import jpyutil
import jpy
import iris


def jvm_init(devroot = None,
             workspace = None,
             propfile = None,
             userHome = None,
             keyfile = None,
             librarypath = None,
             log4jconffile = None,
             workerHeapGB = 12,
             jvmHeapGB = 2,
             verbose = False):
    """ Initialize the JVM to run Illumon Iris.

    devroot -- devroot for Illumon Java installation - must include trailing path separator
    workspace -- Java workspace directory
    propfile -- Illumon Java propfile
    userHome -- User's home directory
    keyfile -- path to private key file for Iris user authentication
    librarypath -- Java library path
    log4jconffile -- Log4j config file
    workerHeapGB -- desired worker heap
    jvmHeapGB -- Desired jvm heap
    verbose -- enable / disable verbose output
    """

    # setup defaults

    if devroot == None:
        devroot = os.environ["ILLUMON_DEVROOT"]

    if not os.path.isdir(devroot):
        raise Exception("idb.init: devroot=%s does not exist."%devroot)

    if verbose:
        print("idb.init: devroot = %s"%devroot)

    if workspace == None:
        workspace = os.environ["ILLUMON_WORKSPACE"]

    if verbose:
        print("idb.init: workspace = %s"%workspace)

    if not os.path.isdir(workspace):
        if verbose:
            print("idb.init: Creating workspace folder (%s)"%workspace)

        os.makedirs(workspace)

    if propfile == None:
        propfile = os.environ["ILLUMON_PROPFILE"]

    if verbose:
        print("idb.init: propfile = %s"%propfile)

    username = os.environ["USERNAME"] if "USERNAME" in os.environ else os.environ["USER"] if "USER" in os.environ else None

    if userHome == None:
        userHome = "W:/home/%s/"%(username)
    else:
        userHome = "%s/"%userHome

    if verbose:
        print("idb.init: userHome = %s"%userHome)

    if keyfile == None:
        keyfile = "%s/priv-%s.base64.txt"%(userHome, username)

    if verbose:
        print("idb.init: keyfile = %s"%keyfile)

    if not os.path.isfile(keyfile):
        raise Exception("idb.init: keyfile=%s does not exist."%keyfile)

    if log4jconffile == None:
        log4jconffile = "%s/log4j.xml"%userHome

    if verbose:
        print("idb.init: log4jconffile = %s"%log4jconffile)

    if verbose:
        print("idb.init: librarypath = %s"%librarypath)
        print("idb.init: workerHeapGB = %s"%workerHeapGB)
        print("idb.init: jvmHeapGB = %s"%jvmHeapGB)

    # setup environment

    jProperties = {
        'workspace': workspace,
        'Configuration.rootFile': propfile,
        'devroot': devroot,
        'disable.jvmstatus': 'true',
        'RemoteProcessingRequest.defaultQueryHeapMB': str(workerHeapGB * 1024),
        'useLongClientDelayThreshold': 'true',
        'WAuthenticationClientManager.defaultPrivateKeyFile': keyfile
    }

    if librarypath != None:
        jProperties['java.library.path'] = librarypath

    if os.path.isfile(log4jconffile):
        jProperties['log4j.configuration'] = 'file:%s'%log4jconffile

    if verbose:
        print("JVM properties...%s"%jProperties)

    jClassPath = [
        '%s/etc'%devroot,
        '%s/Common/config'%devroot,
        '%s/IrisDataObjects/config'%devroot,
        '%s/configs'%devroot,
        '%s/dev-configs'%devroot,
        "%s/%s"%(devroot,'build/classes/main'),
        "%s/%s"%(devroot,'build/resources/main'),
        ]

    jClassPath += glob("%s/*/build/classes/main"%devroot)

    for root,dirs,files in os.walk("%s/%s"%(devroot,'lib')):
        for f in files:
            if f.endswith(".jar"):
                logging.info("JAR %s/%s"%(root,f))
                jClassPath += ["%s/%s"%(root,f)]

    for root,dirs,files in os.walk("%s/build/jars"%(devroot)):
        for f in files:
            if f.endswith(".jar"):
                logging.info("JAR %s/%s"%(root,f))
                jClassPath += ["%s/%s"%(root,f)]

    if verbose:
        print("JVM classpath...%s"%jClassPath)

    jpy.VerboseExceptions.enabled=True

    jpyutil.init_jvm(jvm_maxmem='%sm'%(jvmHeapGB*1024), jvm_properties=jProperties, jvm_classpath=jClassPath, jvm_options=[])

    # Loads our configuration and initializes the class types

    iris.iris()
