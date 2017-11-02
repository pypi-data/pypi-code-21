import os
import csv
from bobo.util import remkdir, isstring, filetail, filebase, quietprint, tolist, islist
from bobo.viset import janus_cs0
import itertools
from bobo.geometry import BoundingBox
from janus.template import GalleryTemplate

def newkey(im):
    return os.path.join('Janus_CS0_frontalized_3d_v1', 'frontalized', '%s_%s.png' % (im.category(), filebase(im.filename())))

def canonicalize(im):
    imf = im.rekey(newkey(im))
    if imf.isvalid():
        imf.bbox = BoundingBox(centroid=(250,250), height=500, width=350)
        return imf
    else:
        return None

def iscanonicalized(im):    
    return im.rekey(newkey(im)).isvalid()
    
def rdd(sparkContext, protocol='A', dataset='train', split=None):
    rdd = janus_cs0.rdd(sparkContext, protocol, dataset, split)
    return rdd.map(lambda im: canonicalize(im) if im.mediatype()=='image' else im.mapFrames(lambda fr: canonicalize(fr)))

def rdd_as_templates(sparkContext, protocol='A', dataset='train', split=None):
    rdd = janus_cs0.rdd_as_templates(sparkContext, protocol, dataset, split)
    return rdd.map(lambda tmpl: GalleryTemplate(media=[canonicalize(im) if canonicalize(im) is not None else im for im in tmpl], mediakeys=tmpl.mediakeys))    

def rdd_as_frontalized(sparkContext, protocol='A', dataset='train', split=None):
    rdd = janus_cs0.rdd_as_templates(sparkContext, protocol, dataset, split)
    return rdd.flatMap(lambda tmpl: [canonicalize(im) for im in tmpl])

    
def splits(sparkContext, protocol='A', split=None, rdd=rdd):
    split = range(1,11) if split is None else split
    return [ [rdd(sparkContext, protocol=protocol, dataset=d, split=s) for d in ['train', 'gallery', 'probe']] for s in tolist(split) ]

def stream(protocol, dataset='train', split=None):
    s = janus_cs0.stream(protocol, dataset, split)
    s_map = itertools.imap(lambda im: canonicalize(im) if im.mediatype()=='image' else im.mapFrames(lambda fr: canonicalize(fr)), s)
    return s_map

