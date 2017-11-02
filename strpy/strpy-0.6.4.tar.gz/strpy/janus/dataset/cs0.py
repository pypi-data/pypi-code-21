import os
import csv
from strpy.bobo.util import remkdir, isstring, filebase, quietprint, tolist, islist, is_hiddenfile
from strpy.bobo.image import ImageDetection
from strpy.bobo.video import VideoDetection
from strpy.janus.template import GalleryTemplate
import strpy.bobo.app
from strpy.bobo.geometry import BoundingBox


class CS0(object):
    def __init__(self, datadir=None, sparkContext=None, f_remapimage=None, appname='janus_cs0', protocoldir=None):
        self.datadir = os.path.join(bobo.app.datadir(), 'Janus_CS0', 'CS0') if datadir is None else datadir
        self.protocoldir = protocoldir if protocoldir is not None else os.path.join(self.datadir, 'protocol')
        if not os.path.isdir(os.path.join(self.datadir)):
            raise ValueError('Download Janus CS0 dataset manually to "%s" ' % self.datadir)
        self.sparkContext = bobo.app.init(appname) if sparkContext is None else sparkContext
        self.f_remapimage = f_remapimage

    def __repr__(self):
        return str('<janus.dataset.cs0: %s>' % self.datadir)

    def splitfile(self, protocol='A', dataset='train', split=None):
        visetdir = os.path.join(self.datadir)
        if split is None:
            csvfile = os.path.join(self.protocoldir, '%s%s.csv' % (dataset, protocol))
        elif protocol is None:
            if dataset == 'gallery':
                csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), 'test_%d_gal.csv' % (int(split)))
            elif dataset == 'probe':
                csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), 'test_%d_probe.csv' % (int(split)))
            elif dataset == 'train':
                csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), 'train_%d.csv' % (int(split)))
        else:
            if dataset == 'gallery':
                csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), 'test_%d_%s_gal.csv' % (int(split), protocol))
            elif dataset == 'probe':
                csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), 'test_%d_%s_probe.csv' % (int(split), protocol))
            elif dataset == 'train':
                csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), 'train_%d_%s.csv' % (int(split), protocol))
        return csvfile

    def subject_id(self):
        subjectdict = {}
        subjectlist = os.listdir(os.path.join(self.datadir, 'subjects'))
        for subject in subjectlist:
            try:
                csvfile = os.path.join(os.path.join(self.datadir, 'subjects'), subject, 'galleryA.csv')
                with open(csvfile, 'rb') as f:
                    x = f.readline().split(',')  # header
                    x = f.readline().split(',')
                    subjectdict[int(x[1])] = subject
            except:
                # ignore invalid directories
                continue
        return subjectdict

    def rdd(self, protocol='A', dataset='train', split=1):
        """Create a resilient distributed dataset from a split file"""
        visetdir = os.path.join(self.datadir)
        csvfile = self.splitfile(protocol, dataset, split)
        subjects = self.subject_id()

        # Parse CSV file based on protocol into RDD of ImageDetection objects, all non-detection properties go in attributes dictionary
        schema = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']
        rdd = (self.sparkContext.textFile(csvfile)
                   .map(lambda row: row.encode('utf-8').split(','))  # CSV to list of row elements
                   .filter(lambda x: x[0] != 'TEMPLATE_ID')  # hack to ignore first row
                   .map(lambda x: ImageDetection(filename=os.path.join(visetdir, x[2]), category=subjects[int(x[1])],
                                            xmin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                                            ymin=float(x[7]) if len(x[7]) > 0 else float('nan'),
                                            xmax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                                            ymax = float(x[7])+float(x[9]) if ((len(x[7])>0) and (len(x[9])>0)) else float('nan'),
                                            attributes={k:v for (k,v) in zip(schema,x)})))  # Parse row into ImageDetection objects

        # Remap image of each detection for different overloaded versions of CS0
        if self.f_remapimage is not None:
            rdd = rdd.map(self.f_remapimage)
        return rdd

    def rdd_as_media(self, protocol='A', dataset='train', split=1):
        """Create a resilient distributed dataset of images and video objects from a split file"""
        return (self.rdd(protocol, dataset, split)
                .keyBy(lambda im: str(im.attributes['SIGHTING_ID']))  # Construct (SIGHTING_ID, x) tuples
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # Construct (SIGHTING_ID, [x1,x2,...,xk]) tuples
                .map(lambda (k,v): tolist(v)[0])  # Remove duplicate sighting IDs
                .keyBy(lambda im: str(im.attributes['MEDIA_ID']))  # Construct (MEDIA_ID, x) tuples for unique sighting ids
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # Group (MEDIA_ID, [x1,x2,...,xk]) tuples
                .map(lambda (k,fr): VideoDetection(frames=fr, attributes={'MEDIA_ID':fr[0].attributes['MEDIA_ID'], 'TEMPLATE_ID':fr[0].attributes['TEMPLATE_ID']}) if len(tolist(fr))>1 else fr))


    def rdd_as_templates(self, protocol='A', dataset='train', split=1):
        """Create a resilient distributed dataset of Gallery Templates from a split file"""
        return (self.rdd(protocol, dataset, split)  # RDD of ImageDetections (im)
                .keyBy(lambda im: '%s_%s' % (str(im.attributes['TEMPLATE_ID']), str(im.attributes['MEDIA_ID'])))  # (TEMPLATEID_MEDIAID, im) keyed by both templateid and mediaid
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # Construct list of media for each template
                .map(lambda (k,fr): VideoDetection(frames=fr, attributes={'MEDIA_ID':fr[0].attributes['MEDIA_ID'], 'TEMPLATE_ID':fr[0].attributes['TEMPLATE_ID']}) if len(tolist(fr))>1 else fr)  # Video or image object for each template
                .keyBy(lambda im: str(im.attributes['TEMPLATE_ID'])) # keyby template id only
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # list of images/videos for each template
                .map(lambda (k,frames): GalleryTemplate(media=frames)))  # construct template as medialist of images and videos assigned to template id

    def as_templates(self, protocol='A', dataset='train', split=1):
        return self.rdd_as_templates(protocol, dataset, split).collect()

    def as_media(self, protocol='A', dataset='train', split=1):
        return self.rdd_as_media(protocol, dataset, split).collect()

    def as_detections(self, protocol='A', dataset='train', split=1):
        return self.rdd(protocol, dataset, split).collect()

    def splits(self, protocol='A', split=None, rdd=rdd):
        """Use provided rdd function to return properly constructed RDDs for all splits"""
        split = range(1,11) if split is None else split
        return [ [rdd(protocol=protocol, dataset=d, split=s) for d in ['train', 'gallery', 'probe']] for s in tolist(split) ]

    def stats(self, protocol='A', dataset='train', split=1):
        rdd = self.rdd_as_media(protocol, dataset, split)
        n_media = rdd.count()
        n_videos = rdd.filter(lambda im: im.mediatype()=='video').count()
        n_images = rdd.filter(lambda im: im.mediatype()=='image').count()
        n_frames = rdd.filter(lambda im: im.mediatype()=='video').flatMap(lambda im: im.frames()).count()
        n_detections = self.rdd(protocol, dataset, split).count()
        n_templates = self.rdd_as_templates(protocol, dataset, split).count()
        return {'protocol':protocol, 'dataset':dataset, 'split':split, 'numMedia':n_media, 'numVideos':n_videos, 'numImages':n_images, 'numFrames':n_frames,'numDetections':n_detections, 'numTemplates':n_templates}


class CS0_2d_v1(CS0):
    def __init__(self, cs0dir=None, newdatadir=None, sparkContext=None):
        cs0dir = os.path.join(bobo.app.datadir(), 'Janus_CS0') if cs0dir is None else cs0dir
        newdatadir = os.path.join(bobo.app.datadir(), 'Janus_CS0_frontalized_2d_affine') if newdatadir is None else newdatadir
        f_remapimage = (lambda im:  im.clone()
                                     .filename(os.path.join(newdatadir, 'frontalized', '%s_%s.png' % (im.category(), filebase(im.filename()))))
                                     .boundingbox(bbox=BoundingBox(centroid=(250,250), height=500, width=350))
                                     if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_%s.png' % (im.category(), filebase(im.filename()))))
                                     else im)
        super(CS0_2d_v1, self).__init__(datadir=os.path.join(cs0dir, 'CS0'), sparkContext=sparkContext, f_remapimage=f_remapimage)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs0_2d_v1: %s>' % self.newdatadir)


class CS0_frontalized_v1(CS0):
    def __init__(self, cs0dir=None, newdatadir=None, sparkContext=None):
        cs0dir = os.path.join(bobo.app.datadir(), 'Janus_CS0') if cs0dir is None else cs0dir
        newdatadir = os.path.join(bobo.app.datadir(), 'Janus_CS0_frontalized_3d_v1') if newdatadir is None else newdatadir
        f_remapimage = (lambda im:  im.clone()
                                     .filename(os.path.join(newdatadir, 'frontalized', '%s_%s.png' % (im.category(), filebase(im.filename()))))
                                     .boundingbox(bbox=BoundingBox(centroid=(250,250), height=500, width=350))
                                     if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_%s.png' % (im.category(), filebase(im.filename()))))
                                     else im)
        super(CS0_frontalized_v1, self).__init__(datadir=os.path.join(cs0dir, 'CS0'), sparkContext=sparkContext, f_remapimage=f_remapimage)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs0_frontalized_v1: %s>' % self.newdatadir)


class CS0_frontalized_v3(CS0):
    def __init__(self, cs0dir=None, newdatadir=None, sparkContext=None):
        cs0dir = os.path.join(bobo.app.datadir(), 'Janus_CS0') if cs0dir is None else cs0dir
        newdatadir = os.path.join(bobo.app.datadir(), 'Janus_CS0_frontalized_3d_v3') if newdatadir is None else newdatadir
        f_remapimage = (lambda im:  im.clone()
                                     .filename(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     .boundingbox(bbox=BoundingBox(centroid=(250,250), height=500, width=350))
                                     if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     else im)
        super(CS0_frontalized_v3, self).__init__(datadir=os.path.join(cs0dir, 'CS0'), sparkContext=sparkContext, f_remapimage=f_remapimage)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs0_frontalized_v3: %s>' % self.newdatadir)


class CS0_frontalized_v41(CS0):
    def __init__(self, cs0dir=None, newdatadir=None, sparkContext=None):
        cs0dir = os.path.join(bobo.app.datadir(), 'Janus_CS0') if cs0dir is None else cs0dir
        newdatadir = os.path.join(bobo.app.datadir(), 'Janus_CS0_frontalized_3d_v4a') if newdatadir is None else newdatadir
        f_remapimage = (lambda im:  im.clone()
                                     .filename(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     .boundingbox(bbox=BoundingBox(centroid=(250,250), height=500, width=350))
                                     if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     else im)
        super(CS0_frontalized_v41, self).__init__(datadir=os.path.join(cs0dir, 'CS0'), sparkContext=sparkContext, f_remapimage=f_remapimage)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs0_frontalized_v41: %s>' % self.newdatadir)


class CS0_frontalized_v42(CS0):
    def __init__(self, cs0dir=None, newdatadir=None, sparkContext=None):
        cs0dir = os.path.join(bobo.app.datadir(), 'Janus_CS0') if cs0dir is None else cs0dir
        newdatadir = os.path.join(bobo.app.datadir(), 'Janus_CS0_frontalized_3d_v4b') if newdatadir is None else newdatadir
        f_remapimage = (lambda im:  im.clone()
                                     .filename(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     .boundingbox(bbox=BoundingBox(centroid=(250,250), height=500, width=350))
                                     if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     else im)
        super(CS0_frontalized_v42, self).__init__(datadir=os.path.join(cs0dir, 'CS0'), sparkContext=sparkContext, f_remapimage=f_remapimage)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs0_frontalized_v42: %s>' % self.newdatadir)
