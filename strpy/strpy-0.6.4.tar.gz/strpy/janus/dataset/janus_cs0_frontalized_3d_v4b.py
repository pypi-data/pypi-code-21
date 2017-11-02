from bobo.viset import janus_cs0_frontalized_3d

VERSION = '4b'

def rdd(sparkContext, protocol='A', dataset='train', split=None):
    return janus_cs0_frontalized_3d.rdd(sparkContext, protocol, dataset, split, version=VERSION)

def rdd_as_templates(sparkContext, protocol='A', dataset='train', split=None):
    return janus_cs0_frontalized_3d.rdd_as_templates(sparkContext, protocol, dataset, split, version=VERSION)

def rdd_as_frontalized(sparkContext, protocol='A', dataset='train', split=None):
    return janus_cs0_frontalized_3d.rdd_as_frontalized(sparkContext, protocol, dataset, split, version=VERSION)
    
def splits(sparkContext, protocol='A', split=None, rdd=rdd):
    return janus_cs0_frontalized_3d.splits(sparkContext, protocol, split, rdd)

def stream(protocol, dataset='train', split=None):
    return janus_cs0_frontalized_3d.stream(protocol, dataset, split, version=VERSION)

