import os
import subprocess
from bobo.util import loadmat, tempyaml
import bobo.app

COMPONENT = 'sample_component'
componentpath = os.path.join(bobo.app.componentpath(),COMPONENT)

def random_vector(im):
    yamlfile = tempyaml()
    cmd = '%s --yaml=%s' % (componentpath, yamlfile)
    print '[janus.sample_component]: executing "%s" ' % cmd
    if subprocess.call(cmd, shell=True) != 0:
        raise IOError('ERROR - running component "%s" ' % COMPONENT)
    print '[janus.sample_component]: loading random vector from "%s" to numpy array ' % yamlfile
    x = loadmat(yamlfile)
    os.remove(yamlfile)
    return x

def imprint(im):
    cmd = '%s --image=%s ' % (componentpath, im.filename())
    print '[janus.sample_component]: executing "%s" ' % cmd
    if subprocess.call(cmd, shell=True) != 0:
        raise IOError('ERROR - running component "%s" ' % COMPONENT)
    return im
    
    
def imshow(imfile):
    cmd = '%s --image=%s --show' % (componentpath, imfile)
    print '[janus.sample_component]: executing "%s" ' % cmd
    if subprocess.call(cmd, shell=True) != 0:
        raise IOError('ERROR - running component "%s" ' % COMPONENT)
    return imfile

