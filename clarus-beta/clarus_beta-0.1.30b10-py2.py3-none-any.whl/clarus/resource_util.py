from six.moves import urllib
import six
import os
import requests
import logging
from clarus.api_config import ApiConfig

#DIRECTORY    = 'c:/clarusft/data/test/'            # where to look for data files

logger = logging.getLogger(__name__)

def openFile(fileName, mode='r'):
    if (os.path.isfile(fileName)) :
        return open(fileName, mode)
    if os.path.isdir(ApiConfig.resource_path):
        fileName = ApiConfig.resource_path+fileName
    return open(fileName, mode)
        
def read(fileNames):
    if 'CHARM_RESOURCE_PATH' in os.environ:
        resourcePath = os.environ['CHARM_RESOURCE_PATH']
        return readResources(fileNames, resourcePath);
    else:
        return readFiles(fileNames);

def readFiles(fileNames):
    streams = []
    
    if isinstance(fileNames, six.string_types):
        fileNameList = fileNames.split(',');
    else:
        fileNameList = fileNames
    
    for fileName in fileNameList:
        try:
            with openFile(fileName.strip()) as f:
                streams.append(f.read())
        except IOError as error:
            logger.error("Error can't open file " + fileName)
            raise error
    return streams;

def readResources(resourceNames, resourcePath):
    streams = []
    
    if isinstance(resourceNames, six.string_types):
        resourceNameList = resourceNames.split(',');
    else:
        resourceNameList = resourceNames
        
    for resourceName in resourceNameList:
        resource = readResource(resourceName, resourcePath)
        if resource is not None:
            streams.append(resource);
        else:
            raise IOError('Cannot open resource '+resourceName)
    return streams;

def readResource(resourceName, resourcePath):
    if resourcePath.startswith('http'):
        return readHttpResource(resourceName, resourcePath)
    else:
        return None

def readHttpResource(resourceName, resourcePath):
    url = resourcePath + urllib.parse.quote_plus(resourceName)
    logger.debug ('reading http resource '+url)
    r = requests.get(url)
    if r.status_code != 200:
        logger.error ('error reading http resource: '+str(r.status_code)+" " + r.text)
        return None
    else:
        return r.text

def write(fileName, data):
    try:
        f = openFile(fileName.strip(), 'w')
        f.write(data.text)
    except IOError as error:
        logger.error ("Error can't open file " + fileName);
        raise error