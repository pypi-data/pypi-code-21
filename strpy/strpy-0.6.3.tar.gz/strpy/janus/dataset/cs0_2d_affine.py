import os
import csv
from bobo.util import remkdir, isstring, filetail, filebase, quietprint, tolist, islist
from bobo.viset import janus_cs0
import itertools
from bobo.geometry import BoundingBox
from janus.template import GalleryTemplate

def newfilename(im):
    imfile = os.path.join('Janus_CS0_frontalized_2d_affine', 'frontalized', '%s_%s.png' % (im.category(), filebase(im.filename())))
    return im.clone().filename(imfile)

def frontalize(im):
    imf = newfilename(im)
    if im.mediatype() == 'image':
        if imf.isvalid():
            imf.bbox = BoundingBox(centroid=(250,250), height=500, width=350)
            return imf
        else:
            return None
    

def isfrontalized(im):    
    return newfilename(im).isvalid()
    
def rdd(sparkContext, protocol='A', dataset='train', split=None, datadir=None):
    rdd = janus_cs0.rdd(sparkContext, protocol, dataset, split, datadir)
    return rdd.map(lambda im: frontalize(im))  # imagedetections

def rdd_as_media(sparkContext, protocol='A', dataset='train', split=None, datadir=None):
    rdd = janus_cs0.rdd_as_media(sparkContext, protocol, dataset, split, datadir)
    return rdd.map(lambda im: frontalize(im))  # imagedetections
    
    
def rdd_as_templates(sparkContext, protocol='A', dataset='train', split=None):
    rdd = janus_cs0.rdd_as_templates(sparkContext, protocol, dataset, split)
    return rdd.map(lambda tmpl: GalleryTemplate(media=[frontalize(im) if frontalize(im) is not None else im for im in tmpl], mediakeys=tmpl.mediakeys))
    #return rdd.map(lambda tmpl: frontalize(tmpl.media[0]))
    #return rdd.map(lambda tmpl: newkey(tmpl.media[0]))    

def rdd_as_frontalized(sparkContext, protocol='A', dataset='train', split=None):
    rdd = janus_cs0.rdd_as_templates(sparkContext, protocol, dataset, split)
    return rdd.flatMap(lambda tmpl: [frontalize(im) for im in tmpl])
    #return rdd.map(lambda tmpl: frontalize(tmpl.media[0]))
    #return rdd.map(lambda tmpl: newkey(tmpl.media[0]))    
        
def splits(sparkContext, protocol='A', split=None, rdd=rdd):
    split = range(1,11) if split is None else split
    return [ [rdd(sparkContext, protocol=protocol, dataset=d, split=s) for d in ['train', 'gallery', 'probe']] for s in tolist(split) ]

def stream(protocol, dataset='train', split=None):
    s = janus_cs0.stream(protocol, dataset, split)
    s_map = itertools.imap(lambda im: frontalize(im) if im.mediatype()=='image' else im.mapFrames(lambda fr: frontalize(fr)), s)
    return s_map
    
def stats(sparkContext, protocol, dataset='train', split=None):
    rdd = janus_cs0.rdd(sparkContext, protocol, dataset, split)
    n_media = rdd.count()
    n_videos = rdd.filter(lambda im: im.mediatype()=='video').count()
    n_images = rdd.filter(lambda im: im.mediatype()=='image').count() 
    n_frames = rdd.map(lambda v: len(v) if v.mediatype()=='video' else 0).sum()               
    n_detections = rdd.map(lambda v: len(v) if v.mediatype()=='video' else 1).sum()            
    n_images_frontalized = rdd.filter(lambda im: isfrontalized(im) if im.mediatype()=='image' else False).count()
    n_frames_frontalized = rdd.map(lambda v: len(v.filterFrames(lambda fr: isfrontalized(fr))) if v.mediatype()=='video' else 0).sum()
    n_detections_frontalized = n_images_frontalized + n_frames_frontalized
    frontalizationRate = '%1.3f' % ((float(n_detections_frontalized)/float(n_detections)) if n_detections>0 else 0.0)
    imageFrontalizationRate = '%1.3f' % ((float(n_images_frontalized)/float(n_images)) if n_images>0 else 0.0)
    frameFrontalizationRate = '%1.3f' % ((float(n_frames_frontalized)/float(n_frames)) if n_frames>0 else 0.0)
    
    return {'numMedia':n_media, 'numVideos':n_videos, 'numImages':n_images, 'numFrames':n_frames,'numDetections':n_detections,
            'numImagesFrontalized':n_images_frontalized, 'numFramesFrontalized':n_frames_frontalized, 'frontalizationRate':frontalizationRate,
            'imageFrontalizationRate':imageFrontalizationRate, 'frameFrontalizationRate':frameFrontalizationRate}

