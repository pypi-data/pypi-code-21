###############################################################################
#
# Copyright (c) 2011 Projekt01 GmbH and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
###############################################################################

__docformat__ = "reStructuredText"

import os
import os.path
import zipfile

import shutil
import fnmatch
import time
import tempfile
import urllib
import socket
import subprocess
import setuptools.archive_util

import yaml
import json

VERSION = '5.6.3'
BASE = 'https://artifacts.elastic.co/downloads/elasticsearch'

elasticSearchProcess = None

# helper for zip and unzip data for simpler sample data setup
def zipFolder(folderPath, zipPath, topLevel=False):
    """Zip a given folder to a zip file, topLevel stores top elvel folder too"""
    # remove existing zip file
    if os.path.exists(zipPath):
        os.remove(zipPath)
    zip = zipfile.ZipFile(zipPath, 'w', zipfile.ZIP_DEFLATED)
    path = os.path.normpath(folderPath)
    # os.walk visits every subdirectory, returning a 3-tuple of directory name,
    # subdirectories in it, and filenames in it
    for dirPath, dirNames, fileNames in os.walk(path):
        # walk over every filename
        for file in fileNames:
            # ignore hidden and lock files
            if not (file.startswith('.') or file.endswith('.lock')):
                if topLevel:
                    fPath = os.path.join(dirPath, file)
                    relPath = os.path.join(dirPath, file)[len(path)+len(os.sep):]
                    arcName = os.path.join(os.path.basename(path), relPath)
                    zip.write(fPath, arcName)
                else:
                    fPath = os.path.join(dirPath, file)
                    relPath = os.path.join(dirPath[len(path):], file)
                    zip.write(fPath, relPath)
    zip.close()
    return None


def unZipFile(zipPath, target):
    # If the output location does not yet exist, create it
    if not os.path.isdir(target):
        os.makedirs(target)
    zip = zipfile.ZipFile(zipPath, 'r')
    for each in zip.namelist():
        # check to see if the item was written to the zip file with an
        # archive name that includes a parent directory. If it does, create
        # the parent folder in the output workspace and then write the file,
        # otherwise, just write the file to the workspace.
        if not each.endswith('/'):
            root, name = os.path.split(each)
            directory = os.path.normpath(os.path.join(target, root))
            if not os.path.isdir(directory):
                os.makedirs(directory)
            file(os.path.join(directory, name), 'wb').write(zip.read(each))
    zip.close()


# support missing ignore pattern in py25
def ignore_patterns(*patterns):
    """Function that can be used as copytree() ignore parameter"""
    def _ignore_patterns(path, names):
        ignored_names = []
        for pattern in patterns:
            ignored_names.extend(fnmatch.filter(names, pattern))
        return set(ignored_names)
    return _ignore_patterns


def copytree(src, dst, ignore=None):
    """Recursively copy a directory tree using copy2()"""
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if os.path.isdir(srcname):
                copytree(srcname, dstname, ignore)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors

def isOpen(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(1)
        s.connect((ip, int(port)))
        s.shutdown(2)
        s.close()
        return True
    except socket.error:
        return False

def portSplit(port):
    """
    Splits a port range given as a string into a list of
    integer ports. If no range is given, return a list with
    only one integer port.
    A range like '9200-9300' will *not* return the port 9300,
    as port ranges would overlap in the usual config files.
    """
    if isinstance(port, int):
        return [port]
    elif '-' not in port:
        return [ int(port) ]
    else:
        low, high = port.split('-')
        low = int(low.strip())
        high = int(high.strip())
        return range(low, high)

def readConfFile(confDir):
    """
    Find the config file in the conf dir and parse it
    The config file is either elasticsearch.yml or elasticsearch.json.
    Return a dictionary as parsed from the respective parser
    """
    jsonFile = os.path.join(confDir, 'elasticsearch.json')
    yamlFile = os.path.join(confDir, 'elasticsearch.yml')
    if os.path.exists(jsonFile):
        confFile = jsonFile
        confLoad = json.load
    else:
        confFile = yamlFile
        confLoad = yaml.load
    with open(confFile) as stream:
        config = confLoad(stream)
    return config

def parseConf(config):
    """
    Find host and port from the config data.
    If a value isn't there, default values are used.
    """
    if config is None:
        config = {}
    httpPort = portSplit(config.get('http',
        {'port':'9200-9300'})['port'])
    transportPort = portSplit(config.get('transport',
        {'tcp':{'port':'9300-9400'}})['tcp']['port'])
    host = config.get('network',
        {'host':'localhost'})['host']
    clusterName = config.get('cluster',
        {'name':'es-testing'})['name']
    config = {
        'httpPort': httpPort,
        'transportPort': transportPort,
        'host': host,
        'clusterName': clusterName,
    }
    return config

def startElasticSearchServer(sandBoxDir=None, dataDir=None, logDir=None,
    confSource=None, dataSource=None, mappingSource=None, javaOptions=None,
    sleep=1, sleepCopy=3, downloadURL=None, version=VERSION,
    confSourceCopyTreeIgnorePatterns='*.svn',
    dataSourceCopyTreeIgnorePatterns='*.svn',
    mappingSourceCopyTreeIgnorePatterns='*.svn'):
    """Start the elasticsearch test server."""

    # setup server (ES_HOME) dir path
    if sandBoxDir is None:
        here = os.path.dirname(__file__)
        sandbox = os.path.join(here, 'sandbox')
    else:
        sandbox = sandBoxDir

    # setup data dir
    if dataDir is None:
        data = os.path.join(sandbox, 'data')
    else:
        data = dataDir

    # setup logs dir
    if logDir is None:
        logs = os.path.join(sandbox, 'logs')
    else:
        logs = logDir

    # setup config, data and logs dir path
    conf = os.path.join(sandbox, 'config')
    mapping = os.path.join(sandbox, conf, 'mappings')

    # if we didn't found a elastic search server location, let's download the
    # latest stable version and store it in a folder called sandbox in our
    # package location
    # Note: make sure you have the permission to run the server under this
    # location!
    if not os.path.exists(sandbox):
        # create server location
        os.mkdir(sandbox)

    # download and install a server
    names = os.listdir(sandbox)
    if not 'lib' in names and not 'bin' in names:
        if downloadURL is None:
            # windows
            if os.name == 'nt':
                url = '%s/elasticsearch-%s.zip' % (BASE, version)
            # non windows
            else:
                url = '%s/elasticsearch-%s.tar.gz' % (BASE, version)
        else:
            url = downloadURL

        tmpDir = tempfile.mkdtemp('p01-elasticstub-download-tmp')
        handle, downloadFile = tempfile.mkstemp(prefix='p01-elasticstub-download')
        urllib.urlretrieve(url, downloadFile)
        setuptools.archive_util.unpack_archive(downloadFile, tmpDir)
        topLevelDir = os.path.join(tmpDir, os.listdir(tmpDir)[0])
        for fName in os.listdir(topLevelDir):
            source = os.path.join(topLevelDir, fName)
            dest = os.path.join(sandbox, fName)
            shutil.move(source, dest)

    # first remove the original data folder, we need an empty setup
    if os.path.exists(data):
        shutil.rmtree(data)

    # re-use predefined elasticsearch data for simpler testing
    if dataSource is not None and os.path.exists(dataSource):
        if dataSource.endswith('.zip'):
            # extract zip file to dataDir
            try:
                unZipFile(dataSource, data)
            except Exception, e: # WindowsError?, just catch anything
                # this was to early just try again
                time.sleep(sleepCopy)
                if os.path.exists(data):
                    shutil.rmtree(data)
                unZipFile(dataSource, data)
        else:
            ignore = None
            if dataSourceCopyTreeIgnorePatterns is not None:
                ignore = ignore_patterns(dataSourceCopyTreeIgnorePatterns)
            try:
                copytree(dataSource, data, ignore=ignore)
            except Exception, e: # WindowsError?, just catch anything
                # this was to early just try again
                time.sleep(sleepCopy)
                if os.path.exists(data):
                    shutil.rmtree(data)
                copytree(dataSource, data, ignore=ignore)

    # move the given conf source to our config location
    if confSource is not None and os.path.exists(confSource):
        if os.path.exists(conf):
            shutil.rmtree(conf)
        ignore = None
        if confSourceCopyTreeIgnorePatterns is not None:
            ignore = ignore_patterns(confSourceCopyTreeIgnorePatterns)
        copytree(confSource, conf, ignore=ignore)

    # get the host and port out of the config for later use
    config = readConfFile(conf)
    config = parseConf(config)

    # move the given mapping source to our mapping location
    if mappingSource is not None and os.path.exists(mappingSource):
        if os.path.exists(mapping):
            shutil.rmtree(mapping)
        ignore = None
        if mappingSourceCopyTreeIgnorePatterns is not None:
            ignore = ignore_patterns(mappingSourceCopyTreeIgnorePatterns)
        copytree(mappingSource, mapping, ignore=ignore)

    # setup java options and friends
    libPath = os.path.join(sandbox, 'lib')
    esPath = os.path.join(libPath, 'elasticsearch-%s.jar' % version)
    sigarPath = os.path.join(libPath, 'sigar')
    JAVA_HOME = os.environ['JAVA_HOME']
    JAVA_BIN = os.path.join(JAVA_HOME, 'bin', 'java')
    CLASSPATH = os.environ.get('CLASSPATH', '')
    if os.name == 'nt':
        sep = ';'
    else:
        sep = ':' #linux does not like ;
    # ES_CLASSPATH = "%s%s*%s%s%s%s%s*%s%s%s*%s%s" % (libPath, os.sep, sep,
    #     esPath, sep,
    #     libPath, os.sep, sep,
    #     sigarPath, os.sep, sep, CLASSPATH)
    ES_CLASSPATH = "%s%s*" % (libPath, os.sep)

    cmd = [JAVA_BIN]
    if javaOptions is None:
        javaOptions = [
            "-Xms2g",
            "-Xmx2g",
            # "-Djline.enabled=false",
            # "-XX:+UseParNewGC",
            # GC configuration
            "-XX:+UseConcMarkSweepGC",
            "-XX:CMSInitiatingOccupancyFraction=75",
            "-XX:+UseCMSInitiatingOccupancyOnly",
            # "-XX:+CMSParallelRemarkEnabled",
            # heap dumps
            "-XX:+HeapDumpOnOutOfMemoryError",
            # pre-touch memory pages used by the JVM during initialization
            "-XX:+AlwaysPreTouch",
            # explicitly set the stack size (reduce to 320k on 32-bit client JVMs)
            "-Xss1m",
            # set to headless, just in case
            "-Djava.awt.headless=true",
            # ensure UTF-8 encoding by default (e.g. filenames)
            "-Dfile.encoding=UTF-8",
            # use our provided JNA always versus the system one
            "-Djna.nosys=true",
            # use old-style file permissions on JDK9
            "-Djdk.io.permissionsUseCanonicalPath=true",
            # flags to configure Netty
            "-Dio.netty.noUnsafe=true",
            "-Dio.netty.noKeySetOptimization=true",
            "-Dio.netty.recycler.maxCapacityPerThread=0",
            # log4j 2
            "-Dlog4j.shutdownHookEnabled=false",
            "-Dlog4j2.disable.jmx=true",
            "-Dlog4j.skipJansi=true",
           ]
    cmd += javaOptions
    cmd += [
        "-Delasticsearch",
        "-Des-foreground=yes",
        "-Des.path.home=%s" % sandbox,
        "-Des.path.data=%s" % data,
        "-Des.path.conf=%s" % conf,
        "-Des.path.logs=%s" % logs,
        "-cp", ES_CLASSPATH, "org.elasticsearch.bootstrap.Elasticsearch",
        ]

    # and start the elasticsearch stub server
    try:
        p = subprocess.Popen(cmd, shell=False)
    except Exception, e:
        raise Exception("Subprocess error: %s" % e)

    global elasticSearchProcess
    elasticSearchProcess = p

    # wait some time for the elasticsearch server port to open
    httpPort = config['httpPort'][0]
    for i in range(16):
        time.sleep(1)
        if isOpen(config['host'],httpPort):
            break
    time.sleep(sleep) # give it the extra wait time, from the arguments

def stopElasticSearchServer(sleep=1):
    # terminate our elasticsearch server
    global elasticSearchProcess
    # p.terminate() should work on windows + posix since py 2.6
    elasticSearchProcess.terminate()
    elasticSearchProcess.wait()
    elasticSearchProcess = None
    time.sleep(sleep)


###############################################################################
#
# Doctest setup
#
###############################################################################

def doctestSetUp(test):
    # setup elasticsearch server
    here = os.path.dirname(__file__)
    confSource = os.path.join(here, 'config')
    startElasticSearchServer(confSource=confSource)


def doctestTearDown(test):
    # tear down elasticsearch server
    stopElasticSearchServer()
