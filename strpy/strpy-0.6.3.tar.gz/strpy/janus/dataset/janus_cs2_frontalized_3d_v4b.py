from bobo.viset import janus_cs2_frontalized_3d

VERSION = '4b'

def rdd(sparkContext, dataset='train', split=None):
    return janus_cs2_frontalized_3d.rdd(sparkContext, dataset, split, version=VERSION)

def rdd_as_templates(sparkContext, dataset='train', split=None):
    return janus_cs2_frontalized_3d.rdd_as_templates(sparkContext, dataset, split, version=VERSION)

def rdd_as_frontalized(sparkContext, dataset='train', split=None):
    return janus_cs2_frontalized_3d.rdd_as_frontalized(sparkContext, dataset, split, version=VERSION)
    
def splits(sparkContext, split=None, rdd=rdd):
    return janus_cs2_frontalized_3d.splits(sparkContext, split, rdd)

def stream(dataset='train', split=None):
    return janus_cs2_frontalized_3d.stream(dataset, split, version=VERSION)

