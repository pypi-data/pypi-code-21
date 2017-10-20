import os
from strpy.janus.dataset.cs0 import CS0
import strpy.bobo.app
from strpy.bobo.util import remkdir, isstring, filebase, quietprint, tolist, islist, is_hiddenfile, readcsv
from strpy.bobo.image import ImageDetection
from strpy.bobo.video import VideoDetection
from strpy.janus.template import GalleryTemplate
from strpy.bobo.geometry import BoundingBox
from itertools import product, groupby
from collections import OrderedDict


def uniq_cs2_id(im):
    return '%s_%s' % (im.attributes['SIGHTING_ID'], os.path.basename(im.filename()).split('.')[0])


class CS2(object):
    def __init__(self, datadir=None, sparkContext=None, f_remapimage=None, appname='janus_cs2', protocoldir=None, partitions=None):
        self.datadir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2', 'CS2') if datadir is None else os.path.join(datadir, 'Janus_CS2', 'CS2')
        self.protocoldir = protocoldir if protocoldir is not None else os.path.join(self.datadir, 'protocol')
        # quietprint('[janus_cs2.CS2] Using protocoldir = %s'%self.protocoldir, 2)  # Commented out
        if not os.path.isdir(os.path.join(self.datadir)):
            raise ValueError('Download Janus CS2 dataset manually to "%s" ' % self.datadir)
        #self.sparkContext = strpy.bobo.app.init(appname) if sparkContext is None else sparkContext
        self.sparkContext = sparkContext
        self.sparkAppname = appname
        self.f_remapimage = f_remapimage
        self.minPartitions = partitions  # spark.default.parallelism if None

    def __repr__(self):
        return str('<janus.dataset.cs2: %s>' % self.datadir)

    def splitfile(self, dataset, split):
        if split is None:
            csvfile = os.path.join(self.protocoldir, '%s.csv' % (dataset))
        if dataset == 'gallery':
            csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), 'gallery_%d.csv' % (int(split)))
        elif dataset == 'probe':
            csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), 'probe_%d.csv' % (int(split)))
        elif dataset == 'train':
            csvfile = os.path.join(self.protocoldir, 'split%d' % int(split), 'train_%d.csv' % (int(split)))
        else:
            raise ValueError('unknown dataset "%s"' % dataset)
        return csvfile

    def subject_id(self):
        subjectdict = {}
        subjectlist = os.listdir(os.path.join(self.datadir, 'subjects'))
        for subject in subjectlist:
            try:
                csvfile = os.path.join(os.path.join(self.datadir, 'subjects'), subject, 'gallery.csv')
                with open(csvfile, 'rb') as f:
                    x = f.readline().split(',')  # header
                    x = f.readline().split(',')
                    subjectdict[int(x[1])] = subject
            except:
                if subject.strip() != 'Icon':
                    print '[janus_cs2.subject_id]: invalid gallery.csv for subject "%s"' % subject
                continue
        return subjectdict

    def subjects(self):
        return [v for (k,v) in self.subject_id().iteritems()]


    def rdd(self, dataset='train', split=1):
        """Create a resilient distributed dataset from a split file"""
        self.sparkContext = strpy.bobo.app.init(self.sparkAppname) if self.sparkContext is None else self.sparkContext  # on demand
        visetdir = os.path.join(self.datadir)
        csvfile = self.splitfile(dataset, split)
        subjects = self.subject_id()

        # Length based schema
        schema_v1 = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']
        schema_v2 = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y', 'FACE_YAW', 'FOREHEAD_VISIBLE', 'EYES_VISIBLE', 'NOSE_MOUTH_VISIBLE', 'INDOOR', 'GENDER', 'SKIN_TONE', 'AGE', 'FACIAL_HAIR']  # newer schema released on 13MAR15

        # Parse CSV file based on protocol into RDD of ImageDetection objects, all non-detection properties go in attributes dictionary
        sc = self.sparkContext
        rdd = (sc.textFile(csvfile, minPartitions=self.minPartitions)
                   .map(lambda row: row.encode('utf-8').split(','))  # CSV to list of row elements
                   .filter(lambda x: x[0] != 'TEMPLATE_ID')  # hack to ignore first row
                   .map(lambda x: ImageDetection(filename=os.path.join(visetdir, x[2]), category=subjects[int(x[1])],
                                            xmin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                                            ymin=float(x[7]) if len(x[7]) > 0 else float('nan'),
                                            xmax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                                            ymax = float(x[7])+float(x[9]) if ((len(x[7])>0) and (len(x[9])>0)) else float('nan'),
                                            attributes={k:v for (k,v) in zip(schema_v1,x)} if len(x)==len(schema_v1) else {k:v for (k,v) in zip(schema_v2,x)})))  # Parse row into ImageDetection objects

        # Remap image of each detection for different overloaded versions of CS2
        if self.f_remapimage is not None:
            f = self.f_remapimage
            rdd = rdd.flatMap(f)
        return rdd

    def rdd_as_media(self, dataset='train', split=1):
        """Create a resilient distributed dataset of images and video objects from a split file"""
        return (self.rdd(dataset, split)
                .keyBy(lambda im: str(im.attributes['SIGHTING_ID']))  # Construct (SIGHTING_ID, x) tuples
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # Construct (SIGHTING_ID, [x1,x2,...,xk]) tuples
                .map(lambda (k,v): tolist(v)[0])  # Remove duplicate sighting IDs
                .keyBy(lambda im: str(im.attributes['MEDIA_ID']))  # Construct (MEDIA_ID, x) tuples for unique sighting ids
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # Group (MEDIA_ID, [x1,x2,...,xk]) tuples
                .map(lambda (k,fr): VideoDetection(frames=fr, attributes={'MEDIA_ID':fr[0].attributes['MEDIA_ID'], 'TEMPLATE_ID':fr[0].attributes['TEMPLATE_ID']}) if len(tolist(fr))>1 else fr))


    def rdd_as_templates(self, dataset='train', split=1):
        """Create a resilient distributed dataset of Gallery Templates from a split file"""
        return (self.rdd(dataset, split)  # RDD of ImageDetections (im)
                .keyBy(lambda im: '%s_%s' % (str(im.attributes['TEMPLATE_ID']), str(im.attributes['MEDIA_ID'])))  # (TEMPLATEID_MEDIAID, im) keyed by both templateid and mediaid
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # Construct list of media for each template
                .map(lambda (k,fr): VideoDetection(frames=fr, attributes={'MEDIA_ID':fr[0].attributes['MEDIA_ID'], 'TEMPLATE_ID':fr[0].attributes['TEMPLATE_ID']}) if len(tolist(fr))>1 else fr)  # Media (video or image) object for each template
                .keyBy(lambda m: str(m.attributes['TEMPLATE_ID'])) # keyby template id only
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # list of images/videos for each template
                .map(lambda (k,medialist): GalleryTemplate(media=tolist(medialist))))  # construct template as medialist of images and videos assigned to template id

    def rdd_as_good_image_templates(self, dataset='train', split=1,len_frames =1 , num_medias =1):
        from janus.pvr.eval_util import cull_bads_from_template
        """Create a resilient distributed dataset of Gallery Templates from a split file"""
        return (self.rdd(dataset, split)  # RDD of ImageDetections (im)
                .keyBy(lambda im: '%s_%s' % (str(im.attributes['TEMPLATE_ID']), str(im.attributes['MEDIA_ID'])))  # (TEMPLATEID_MEDIAID, im) keyed by both templateid and mediaid
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # Construct list of media for each template
                .map(lambda (k,fr): VideoDetection(frames=fr, attributes={'MEDIA_ID':fr[0].attributes['MEDIA_ID'], 'TEMPLATE_ID':fr[0].attributes['TEMPLATE_ID']}) if len(tolist(fr))>1 else fr)  # Media (video or image) object for each template
                .keyBy(lambda m: str(m.attributes['TEMPLATE_ID'])) # keyby template id only
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # list of images/videos for each template
                .map(lambda (k,medialist): GalleryTemplate(media=tolist(medialist)))
                .map(cull_bads_from_template))  # construct template as medialist of images and videos assigned to template id



    def as_sightings(self, dataset, split):
        visetdir = os.path.join(self.datadir)
        subjects = self.subject_id()

        # Length based schema
        schema_v1 = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']
        schema_v2 = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y', 'FACE_YAW', 'FOREHEAD_VISIBLE', 'EYES_VISIBLE', 'NOSE_MOUTH_VISIBLE', 'INDOOR', 'GENDER', 'SKIN_TONE', 'AGE', 'FACIAL_HAIR']  # newer schema released on 13MAR15

        # Import detection
        csv = readcsv(self.splitfile(dataset, split))[1:]
        imdet = [ImageDetection(filename=os.path.join(visetdir, x[2]), category=subjects[int(x[1])],
                             xmin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                             ymin=float(x[7]) if len(x[7]) > 0 else float('nan'),
                             xmax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                             ymax = float(x[7])+float(x[9]) if ((len(x[7])>0) and (len(x[9])>0)) else float('nan'),
                             attributes={k:v for (k,v) in zip(schema_v1,x)} if len(x)==len(schema_v1) else {k:v for (k,v) in zip(schema_v2,x)}) for x in csv]

        # Added ability to augment cs2 set with frontal images, required when calling all_media()
        if self.f_remapimage is not None:
            l_0 = len(imdet)
            imdet = [im  for image in imdet for im in self.f_remapimage(image)]  # flatmap containing all frontal images
            print 'finished augmenting with frontal images ; before and after size %d , %d' % (l_0,len(imdet))

        return imdet

    def as_media(self, dataset, split):
        imdet = self.as_sightings(dataset, split)
        imgroups = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['MEDIA_ID'])]
        return [VideoDetection(frames=fr, attributes={'MEDIA_ID':fr[0].attributes['MEDIA_ID'], 'TEMPLATE_ID':fr[0].attributes['TEMPLATE_ID']}) if len(fr)>1 else fr[0] for fr in imgroups]

    def as_templates(self, dataset, split):
        imdet = self.as_sightings(dataset, split)
        imtmpl = [list(x) for (k,x) in groupby(imdet, key=lambda im: im.attributes['TEMPLATE_ID'])]  # list of sightings for each template
        T = []  # list of templates
        for t in imtmpl:
            immedia = [list(x) for (k,x) in groupby(t, key=lambda im: im.attributes['MEDIA_ID'])]  # list of media for each template
            medialist = [VideoDetection(frames=fr, attributes={'MEDIA_ID':fr[0].attributes['MEDIA_ID'], 'TEMPLATE_ID':fr[0].attributes['TEMPLATE_ID']}) if len(fr)>1 else fr[0] for fr in immedia]  # objects for each template
            T.append(GalleryTemplate(media=medialist))
        return T



    def probeid(self, split):
        return [pid for (j,pid) in enumerate(list(OrderedDict.fromkeys([int(r[0]) for r in readcsv(self.splitfile('probe', split))[1:]])))]  # in csv order

    def galleryid(self, split):
        return [gid for (j,gid) in enumerate(list(OrderedDict.fromkeys([int(r[0]) for r in readcsv(self.splitfile('gallery', split))[1:]])))]  # in csv order

    def all_templates(self):
        T = self.rdd_as_templates('train',1).map(lambda t: (t.templateid(), t))
        for (d,s) in product(['train','probe','gallery'], range(1,11)):
            T = T.union(self.rdd_as_templates(d,s).map(lambda t: (t.templateid(), t)))
        return T.reduceByKey(lambda a,b: a).map(lambda (k,v): v).collect()


    def rdd_all_media(self):
        M = self.rdd_as_media('train',1).map(lambda m: (m.attributes['MEDIA_ID'], m))
        for (d,s) in product(['train','probe','gallery'], range(1,11)):
            M = M.union(self.rdd_as_media(d,s).map(lambda m: (m.attributes['MEDIA_ID'], m)))
        return M.reduceByKey(lambda a,b: a).map(lambda (k,v): v).collect()

    def all_media(self):
        M = []
        for (d,s) in product(['train','probe','gallery'], range(1,11)):
            M = M + [(m.attributes['MEDIA_ID'], m) for m in self.as_media(d,s)]
        return list(OrderedDict(M).values())  # in csv order


    def all_sightings(self):
        M = []
        for (d,s) in product(['train','probe','gallery'], range(1,11)):
            M = M + [(m.attributes['SIGHTING_ID'], m) for m in self.as_sightings(d,s)]
        return list(OrderedDict(M).values())  # in csv order

    def rdd_all_sightings(self):
        M = self.rdd('train',1).map(lambda m: (m.attributes['SIGHTING_ID'], m))
        for (d,s) in product(['train','probe','gallery'], range(1,11)):
            M = M.union(self.rdd(d,s).map(lambda m: (m.attributes['SIGHTING_ID'], m)))
        return M.reduceByKey(lambda a,b: a).map(lambda (k,v): v).collect()

    def splits(self, split=None, rdd=rdd):
        """Use provided rdd function to return properly constructed RDDs for all splits"""
        split = range(1,11) if split is None else split
        return [ [rdd(dataset=d, split=s) for d in ['train', 'gallery', 'probe']] for s in tolist(split) ]

    def stats(self, dataset='train', split=1):
        rdd = self.rdd_as_media(dataset, split)
        n_media = rdd.count()
        n_videos = rdd.filter(lambda im: im.mediatype()=='video').count()
        n_images = rdd.filter(lambda im: im.mediatype()=='image').count()
        n_frames = rdd.filter(lambda im: im.mediatype()=='video').flatMap(lambda im: im.frames()).count()
        n_detections = self.rdd(dataset, split).count()
        n_templates = self.rdd_as_templates(dataset, split).count()
        return {'dataset':dataset, 'split':split, 'numMedia':n_media, 'numVideos':n_videos, 'numImages':n_images, 'numFrames':n_frames,'numDetections':n_detections, 'numTemplates':n_templates}


    def template_stats(self, dataset='train', split=1):
        rdd = self.rdd_as_templates(dataset, split)
        rdd = rdd.map(lambda t: (t.templateid(), t.category(), len(t.images()), len(t.frames())))
        s = {t[0]: {'category': t[1], 'images': t[2], 'frames': t[3]} for t in rdd.collect()}
        return s


class CS2_frontalized_v41(CS2):
    def __init__(self, cs2dir=None, newdatadir=None, sparkContext=None, appname='janus_cs2_v41'):
        cs2dir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2') if cs2dir is None else cs2dir
        newdatadir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2_frontalized_3d_v4a') if newdatadir is None else newdatadir
        print '[janus.dataset.cs2]: CS2 directory = %s' % cs2dir
        print '[janus.dataset.cs2]: 4.2 directory = %s' % newdatadir
        f_remapimage = (lambda im:  im.clone()
                                     .filename(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     .boundingbox(bbox=BoundingBox(centroid=(250,250), height=500, width=350))
                                     if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     else im)
        super(CS2_frontalized_v41, self).__init__(datadir=os.path.join(cs2dir, 'CS2'), sparkContext=sparkContext, f_remapimage=f_remapimage, appname=appname)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs2_frontalized_v41: %s>' % self.newdatadir)


class CS2_frontalized_v42(CS2):
    def __init__(self, cs2dir=None, newdatadir=None, sparkContext=None, appname='janus_cs2_v42'):
        cs2dir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2') if cs2dir is None else cs2dir
        newdatadir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2_frontalized_3d_v4b') if newdatadir is None else newdatadir
        print '[janus.dataset.cs2]: CS2 directory = %s' % cs2dir
        print '[janus.dataset.cs2]: 4.2 directory = %s' % newdatadir
        f_remapimage = (lambda im:  im.clone()
                                     .filename(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     .boundingbox(bbox=BoundingBox(centroid=(250,250), height=500, width=350))
                                     if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     else im)
        super(CS2_frontalized_v42, self).__init__(datadir=os.path.join(cs2dir, 'CS2'), sparkContext=sparkContext, f_remapimage=f_remapimage, appname=appname)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs2_frontalized_v42: %s>' % self.newdatadir)


class CS2_frontalized_v43(CS2):
    """V4.2 frontalization augmented with original image"""
    def __init__(self, cs2dir=None, newdatadir=None, sparkContext=None, appname='janus_cs2_v43'):
        cs2dir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2') if cs2dir is None else cs2dir
        newdatadir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2_frontalized_3d_v4b') if newdatadir is None else newdatadir
        print '[janus.dataset.cs2]: CS2 directory = %s' % cs2dir
        print '[janus.dataset.cs2]: 4.2 directory = %s' % newdatadir
        f_remapimage = (lambda im:  [im.clone(), im.clone()
                                     .filename(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                     .boundingbox(bbox=BoundingBox(centroid=(250,250), height=500, width=350))]
                                      if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_frontalized_wsym.png' % (im.attributes['SIGHTING_ID'])))
                                      else [im])
        super(CS2_frontalized_v43, self).__init__(datadir=os.path.join(cs2dir, 'CS2'), sparkContext=sparkContext, f_remapimage=f_remapimage, appname=appname)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs2_frontalized_v43: %s>' % self.newdatadir)


class CS2_frontalized_v51(CS2):
    def __init__(self, cs2dir=None, newdatadir=None, sparkContext=None, appname='janus_cs2_v51'):
        cs2dir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2') if cs2dir is None else cs2dir
        newdatadir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2_frontalized_v5a') if newdatadir is None else newdatadir
        print '[janus.dataset.cs2]: CS2 directory = %s' % cs2dir
        print '[janus.dataset.cs2]: 5.1 directory = %s' % newdatadir

        # Return a list of detections from each pose, this will be flatMapped in RDD
        f_remapimage = (lambda im:  [im.flush().clone()
                                     .filename(os.path.join(newdatadir, 'frontalized', '%s_yaw_%s_pitch_%s_frontalized.png' % (im.attributes['SIGHTING_ID'], yaw, pitch)))
                                     .boundingbox(bbox=BoundingBox(centroid=(250,250), height=500, width=350))
                                     .setattribute(key='SIGHTING_ID', value='%s_yaw_%s_pitch_%s' % (im.attributes['SIGHTING_ID'], yaw, pitch))  # multiple "sighting ids" per bounding box now
                                     for (yaw,pitch) in product(['-40', '+00','+40'], ['-30','+00','+30'])]
                                     if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_yaw_%s_pitch_%s_frontalized.png' % (im.attributes['SIGHTING_ID'], '+00', '+00')))
                                     else [im])
        super(CS2_frontalized_v51, self).__init__(datadir=os.path.join(cs2dir, 'CS2'), sparkContext=sparkContext, f_remapimage=f_remapimage, appname=appname)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs2_frontalized_v51: %s>' % self.newdatadir)


class CS2_frontalized_v52(CS2):
    def __init__(self, cs2dir=None, newdatadir=None, sparkContext=None, appname='janus_cs2_v52'):
        cs2dir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2') if cs2dir is None else cs2dir
        newdatadir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2_frontalized_v5b') if newdatadir is None else newdatadir
        print '[janus.dataset.cs2]: CS2 directory = %s' % cs2dir
        print '[janus.dataset.cs2]: 5.2 directory = %s' % newdatadir

        # Return a cylindrical frontalized detection for each sighting id
        f_remapimage = (lambda im:  [im.flush().clone()
                                       .filename(os.path.join(newdatadir, 'frontalized', '%s_cylindrical_frontalized.png' % (im.attributes['SIGHTING_ID'])))
                                       .boundingbox(bbox=BoundingBox(centroid=(float(x), 500.0/2.0), height=500, width=350))  # 1051x500
                                       for x in xrange(200,1051-200,20)]  # 33 bounding boxes overlapped by 20 pixels
                                     if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_cylindrical_frontalized.png' % (im.attributes['SIGHTING_ID'])))
                                     else im)
        super(CS2_frontalized_v52, self).__init__(datadir=os.path.join(cs2dir, 'CS2'), sparkContext=sparkContext, f_remapimage=f_remapimage, appname=appname)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs2_frontalized_v52: %s>' % self.newdatadir)


class CS2_frontalized_v53(CS2):
    ''' 9-pose '''
    def __init__(self, cs2dir=None, newdatadir=None, sparkContext=None, appname='janus_cs2_v53'):
        cs2dir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2') if cs2dir is None else cs2dir
        newdatadir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2_frontalized_v5a') if newdatadir is None else newdatadir
        if not os.path.exists(newdatadir):
            raise ValueError('[janus.dataset.cs2]: Alternate data directory does not exist: "%s"' % newdatadir)
        print '[janus.dataset.cs2]: CS2 directory = %s' % cs2dir
        print '[janus.dataset.cs2]: 5.1 directory = %s' % newdatadir

        # Return a list of detections from each pose, this will be flatMapped in RDD
        f_remapimage = (lambda im:  [im.clone()] + [im.flush().clone()
                                     .filename(os.path.join(newdatadir, 'frontalized', '%s_yaw_%s_pitch_%s_frontalized.png' % (im.attributes['SIGHTING_ID'], yaw, pitch)))
                                     .boundingbox(bbox=BoundingBox(centroid=(250,250), height=500, width=350))
                                     .setattribute(key='SIGHTING_ID', value='%s_yaw_%s_pitch_%s' % (im.attributes['SIGHTING_ID'], yaw, pitch))  # multiple "sighting ids" per bounding box now
                                     for (yaw,pitch) in product(['-40', '+00','+40'], ['-30','+00','+30'])]
                                     if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_yaw_%s_pitch_%s_frontalized.png' % (im.attributes['SIGHTING_ID'], '+00', '+00')))
                                     else [im])
        super(CS2_frontalized_v53, self).__init__(datadir=os.path.join(cs2dir, 'CS2'), sparkContext=sparkContext, f_remapimage=f_remapimage, appname=appname)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs2_frontalized_v51: %s>' % self.newdatadir)

class CS2_frontalized_vN(CS2):
    '''frontalized_v7n'''
    def __init__(self, cs2dir=None, newdatadir=None, sparkContext=None,
                     version = 'v7.4',shape = (500,500),
                     appname_prefix='janus_cs2_',anatomical_articulation =None,bad_list = None,raw_only = False):
        cs2dir = os.path.join(strpy.bobo.app.datadir(), 'Janus_CS2') if cs2dir is None else cs2dir
        if not raw_only:
            newdatadir = os.path.join(strpy.bobo.app.datadir(), 'CS2_frontalized_'+version) if newdatadir is None else newdatadir
        else:
            newdatadir = cs2dir if newdatadir is None else newdatadir
        if not os.path.exists(newdatadir):
            raise ValueError('[janus.dataset.cs2]: Alternate data directory does not exist: "%s"' % newdatadir)
        print '[janus.dataset.cs2]: CS2 directory = %s' % cs2dir
        print '[janus.dataset.cs2]:' + version + 'directory = %s' % newdatadir
        self.version = version
        self.appname = appname_prefix + version
        self.anatomical_articulation = anatomical_articulation
        f_frontalized = (lambda im: [im.flush().clone()
                                    .filename(os.path.join(newdatadir, 'frontalized', '%s_yaw_%s_pitch_%s_frontalized.png' % (im.attributes['SIGHTING_ID'], yaw, pitch)))
                                    .boundingbox(bbox=BoundingBox(centroid=(shape[0]/2,shape[1]/2), height=shape[0], width=shape[1]))
                                    .setattribute(key='SIGHTING_ID', value='%s_yaw_%s_pitch_%s' % (im.attributes['SIGHTING_ID'], yaw, pitch))  # multiple "sighting ids" per bounding box now
                                    .setattribute(key='MEDIA_ID', value=im.attributes['MEDIA_ID'])  # multiple "sighting ids" per bounding box now
                                    .setattribute(key='TEMPLATE_ID',value=im.attributes['TEMPLATE_ID'])
                                    .setattribute(key='GOOD', value = 1.0 )  # frontalization was good

                                    for (yaw,pitch) in product(['-40', '+00','+40'], ['-30','+00','+30'])]
                                    if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_yaw_%s_pitch_%s_frontalized.png' % (im.attributes['SIGHTING_ID'], '+00', '+00')))
                                    else [im])
        f_articulation = (lambda im: [im.flush().clone()
                                    .filename(os.path.join(newdatadir, 'frontalized', '%s_%s.png' % (im.attributes['SIGHTING_ID'], articulation_string)))
                                    .boundingbox(bbox=BoundingBox(centroid=(shape[0]/2,shape[1]/2), height=shape[0], width=shape[1]))
                                    .setattribute(key='SIGHTING_ID', value='%s_%s' % (im.attributes['SIGHTING_ID'], articulation_string))  # multiple "sighting ids" per bounding box now
                                    .setattribute(key='MEDIA_ID', value=im.attributes['MEDIA_ID'])  # multiple "sighting ids" per bounding box now
                                    .setattribute(key='TEMPLATE_ID',value=im.attributes['TEMPLATE_ID'])

                                    .setattribute(key='GOOD', value=1.0 )  # multiple "sighting ids" per bounding box now
                                    for articulation_string in anatomical_articulation.capture_strings]
                                    if os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_%s.png' % (im.attributes['SIGHTING_ID'], anatomical_articulation.capture_strings[0])))
                                    else [im])

        f_remap = (lambda im: [im.setattribute(key='GOOD', value=1.0 )] + f_frontalized(im) if anatomical_articulation is None else [im.setattribute(key='GOOD', value=1.0 )] + f_frontalized(im) + f_articulation(im))
        if raw_only:
            f_remap = (lambda im :[im.setattribute(key='GOOD', value=1.0 )])
        f_filter_bads = (lambda im: f_remap(im) if (im.attributes['SIGHTING_ID']) not in bad_list and os.path.isfile(os.path.join(newdatadir, 'frontalized', '%s_yaw_%s_pitch_%s_frontalized.png' % (im.attributes['SIGHTING_ID'], '+00', '+00'))) else im.setattribute(key='GOOD',value=0.0))
        f_remapimage  = f_remap if bad_list is None else f_filter_bads


        super(CS2_frontalized_vN, self).__init__(datadir=os.path.join(cs2dir, 'CS2'), sparkContext=sparkContext, f_remapimage=f_remapimage, appname = self.appname)
        self.newdatadir = newdatadir

    def __repr__(self):
        return str('<janus.dataset.cs2_frontalized_' + self.version +': %s>' % self.newdatadir)
