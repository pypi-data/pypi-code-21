import os
import csv
from glob import glob
from bobo.cache import Cache
from bobo.util import remkdir, isstring, filebase, quietprint, tolist, islist, is_hiddenfile
import bobo.util
from bobo.viset.stream import ImageStream
from bobo.image import ImageDetection
from bobo.video import VideoDetection
from janus.template import GalleryTemplate
from janus.recognition import *
import bobo.app


class GalleryD11(object):
    def __init__(self, galleryname, model, datadir=None):
        """GalleryD11 class: FIXME: Unify T&E workflow with gallery updates"""
        self.templates = {} # templateid : GalleryTemplate
        self.model = model
        self.galleryname = galleryname
        self.datadir = os.path.join(bobo.app.datadir(), 'Janus_Gallery', galleryname) if datadir is None else datadir
        self.csvfile = os.path.join(self.datadir, '%s.csv' % (galleryname))
        self.trainset = {}
        self.galleryset = {}
        self.gallerysvms = {}

    def load(filename, galleryname=None, datadir=None):
        """Create a GalleryD11 from a pickled gallery file, Recognition*, or CompactAndDiscriminativeFaceTrackDescriptor"""
        ref = bobo.util.load(filename)

        if isinstance(ref, GalleryD11):
            galleryname = ref.galleryname if galleryname is None else galleryname
            new = GalleryD11(galleryname=galleryname,
                             model=RecognitionD11(gmm=ref.model.descriptor.gmm, pca=ref.model.descriptor.pca, metric=ref.model.descriptor.metric))
            new.galleryset = ref.galleryset
            new.trainset = ref.trainset
            new.gallerysvms = ref.gallerysvms
            return new

        if isinstance(ref, CompactAndDiscriminativeFaceTrackDescriptor):
            pass
        elif hasattr(ref, 'descriptor'):
            ref = ref.descriptor
        else:
            raise ValueError('Unsupported gallery or model type: %s' % type(ref))
        return GalleryD11(galleryname,
                          model=RecognitionD11(gmm=ref.gmm, pca=ref.pca, metric=ref.metric),
                          datadir=datadir)
    load = staticmethod(load)


    def enroll_template(self, template, template_id):
        """DEPRECATED: Currently used by T&E wrapper"""
        template.enroll( template_id )
        self.templates[template_id] = template


    def flatten_templates(self, templates):
        """DEPRECATED: Currently used by T&E wrapper"""
        flattened_templates = { k:v for (k,v) in templates.map(lambda t: (t[0], t[1].flatten(self.model.f_encoding))).collect() }
        return flattened_templates


    def test(self, probeset, galleryset):
        """DEPRECATED: Currently used by T&E wrapper"""
        (y,yhat) = self.model.test( probeset, galleryset )
        return (y,yhat)


    def rdd(self, sparkContext=None):
        """Create a resilient distributed dataset from a split file"""
        if self.galleryname is None:
            raise ValueError('galleryname is required')
        schema = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']

        # Parse CSV file based on protocol into RDD of ImageDetection objects, all non-detection properties go in attributes dictionary
        schema = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']
        sc = bobo.app.init('janus_gallery') if sparkContext is None else sparkContext
        return (sc.textFile(self.csvfile)
                  .map(lambda row: row.encode('utf-8').split(','))  # CSV to list of row elements
                  .filter(lambda x: x[0] != 'TEMPLATE_ID')  # hack to ignore first row
                  .map(lambda x: ImageDetection(filename=os.path.join(self.datadir, x[2]), category=x[1],
                                                xmin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                                                ymin=float(x[7]) if len(x[7]) > 0 else float('nan'),
                                                xmax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                                                ymax = float(x[7])+float(x[9]) if ((len(x[7])>0) and (len(x[9])>0)) else float('nan'),
                                                attributes={k:v for (k,v) in zip(schema,x)})))  # Parse row into ImageDetection objects


    def rdd_as_templates(self, sparkContext=None):
        """Create a resilient distributed dataset of Gallery Templates from a split file"""
        return (self.rdd(sparkContext=sparkContext)  # RDD of ImageDetections (im)
                .keyBy(lambda m: str(m.attributes['TEMPLATE_ID'])) # keyby template id only
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # list of images/videos for each template
                .map(lambda (k,medialist): GalleryTemplate(media=tolist(medialist))))  # construct template as medialist of images and videos assigned to template id


    def rdd_templates_as_video(self, sparkContext=None):
        """Create a resilient distributed dataset from a split file"""
        return (self.rdd(sparkContext=sparkContext)  # RDD of ImageDetections (im)
                .keyBy(lambda m: str(m.attributes['TEMPLATE_ID'])) # keyby template id only
                .reduceByKey(lambda a,b: tolist(a)+tolist(b))  # list of images/videos for each template
                .map(lambda (k,fr): VideoDetection(frames=tolist(fr), attributes=tolist(fr)[0].attributes)))

    def stream(self):
        def parser(row):
            x = row.encode('utf-8').split(',') if not islist(row) else row  # CSV to list
            schema = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']
            return (ImageDetection(filename=os.path.join(self.datadir, x[2]), category=x[1],
                                   xmin=float(x[6]) if len(x[6]) > 0 else float('nan'),
                                   ymin=float(x[7]) if len(x[7]) > 0 else float('nan'),
                                   xmax = float(x[6])+float(x[8]) if ((len(x[6])>0) and (len(x[8])>0)) else float('nan'),
                                   ymax = float(x[7])+float(x[9]) if ((len(x[7])>0) and (len(x[9])>0)) else float('nan'),
                                   attributes={k:v for (k,v) in zip(schema,x)}))

        return ImageStream(csvfile=self.csvfile, parser=parser, delimiter=',', rowstart=2) 

    def nextSightingId(self):
        """Return the next value to be used for a new sighting"""
        nextid = 0
        if os.path.exists(self.csvfile):
            with open(self.csvfile, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        sightingid = int(row['SIGHTING_ID'])
                        nextid = max(nextid, (sightingid))
                    except ValueError:
                        pass

        return nextid+1


    def enroll(self, sparkContext, template, encode=True, f_preprocess=None):
        """Create or update gallery metadata and image cache with a list of images"""
        imgdir = os.path.join(self.datadir, 'img')
        remkdir(imgdir)
        schema = ['TEMPLATE_ID', 'SUBJECT_ID', 'FILE', 'MEDIA_ID', 'SIGHTING_ID', 'FRAME', 'FACE_X', 'FACE_Y', 'FACE_WIDTH', 'FACE_HEIGHT', 'RIGHT_EYE_X', 'RIGHT_EYE_Y', 'LEFT_EYE_X', 'LEFT_EYE_Y', 'NOSE_BASE_X', 'NOSE_BASE_Y']

        sighting_id = self.nextSightingId()

        if not os.path.exists(self.csvfile):
            with open(self.csvfile, 'w') as f:
                writer = csv.DictWriter(f, fieldnames=schema)
                writer.writeheader()

        with open(self.csvfile, 'a') as f:
            writer = csv.DictWriter(f, fieldnames=schema)
            for x in template:
                items = x if hasattr(x, '__iter__') else [x]
                for im in items:
                    if im.attributes is None:
                        im.attributes = { 'TEMPLATE_ID': im.category(), 'SUBJECT_ID': im.category() }
                    filename = os.path.join(imgdir, '%08d.png' % sighting_id)
                    im.attributes['FILE'] = filename
                    im.attributes['SIGHTING_ID'] = str(sighting_id)
                    sighting_id += 1
                    im.saveas(filename)

                    if filename.startswith(self.datadir):
                        filename = filename[len(self.datadir):].lstrip('/')
                    r = {}
                    for (k, v) in im.attributes.iteritems():
                        if k in schema:
                            r[k] = v
                    r['FILE'] = filename # Write out path relative to csv file
                    writer.writerow(r)

        if encode:
            print '[janus.gallery.enroll] encoding gallery as media'
            category = template.category()
            f_preprocess = f_preprocess if f_preprocess is not None else self.model.preprocess
            f_encoding = self.model.descriptor.encode
            galleryset = sparkContext.parallelize([template.map(f_preprocess)])
            galleryset = (galleryset.flatMap(lambda t: t.media())
                                    .map(lambda m: f_encoding(m).flatten())
                                    .collect())

            if category in self.galleryset:
                self.galleryset[category] = self.galleryset[category] + tuple(galleryset)
            else:
                self.galleryset[category] = tuple(galleryset)

        return self


    def trainsvms(self, sparkContext=None, trainset=None, use_gallery_negatives=True, ignore_empty_trainset=False):
        '''Train one-vs-rest linear SVM classifiers for the gallery, using trainset and opposing gallery members as the negative sets.
        Trainset should be pre-processed.'''
        if trainset is not None:
            f_encoding = self.model.descriptor.encode
            print '[janus.gallerysvm.encode] collecting train as media'
            trainset =  (trainset.flatMap(lambda t: t.media())
                                 .map(lambda m: (m.category(), f_encoding(m).flatten()))
                                 .keyBy(lambda m: m[0])
                                 .reduceByKey(lambda a,b: (a,)+(b,))
                                 .collect())
            self.trainset = {c:v for c,v in trainset.iteritems()}
        elif ignore_empty_trainset == False and len(self.trainset) == 0:
            raise ValueError('[janus.gallery.trainsvms]: The trainset is empty: no negative examples!')

        if len(self.galleryset) == 0:
            raise ValueError('[janus.gallery.trainsvms]: The galleryset is empty - no subjects have been enrolled!')

        sc = trainset.context if trainset is not None else None
        sc = sc if sc is not None else sparkContext
        if sc is None:
            raise ValueError('[janus.gallery.trainsvms]: Either sparkContext or trainset must be provided!')

        if len(self.trainset) > 0:
            Tc, T = zip(*[(k,x) for (k,v) in self.trainset.iteritems() for x in v])
        else:
            Tc = T = None

        Gc, G = zip(*[(k,x) for (k,v) in self.galleryset.iteritems() for x in v])
        subjects, svms = self.model.trainsvms(sparkContext=sc, trainset=(Tc, T), galleryset=(Gc, Gc, G))
        self.gallerysvms = {k:v for k,v in zip(subjects, svms)}
        return self


    def svmidentify(self, probetemplate):
        if len(self.gallerysvms) != len(self.galleryset):
            raise ValueError('[janus.gallery.trainsvms]: Not all gallery subjects [%d] have SVMs [%d] trained!' % (len(self.galleryset), len(self.gallerysvms)))
        if len(self.gallerysvms) == 0:
            raise ValueError('[janus.gallery.trainsvms]: Not SVMs trained for gallery subject! Call trainsvms first.')

        t = probetemplate
        f_encoding = self.model.descriptor.encode
        (Pid, Pc, P) = zip(*[(t.templateid(), t.category(), f_encoding(m).flatten()) for m in t.media()])
        Gc, G = zip(*[(k,x) for (k,v) in self.galleryset.iteritems() for x in v])
        # Sort highest score first
        (y, yhat, n_gallery, s) = self.model.testsvmsingle(probeset=(Pid, Pc, P), galleryset=(Gc, G), gallerysvms=self.gallerysvms)
        (y, yhat, s) = zip(*sorted(zip(y.flatten(), yhat.flatten(), s), key=lambda x: x[1], reverse=True))
        return (y, yhat, n_gallery, s)


    def testsvm(self, probeset, probesvms=None):
        if len(self.gallerysvms) != len(self.galleryset):
            raise ValueError('Not all gallery subjects [%d] have SVMs [%d] trained!' % (len(self.galleryset), len(self.gallerysvms)))
        if len(self.gallerysvms) == 0:
            raise ValueError('Not SVMs trained for gallery subject! Call trainsvms first.')

        sc = probeset.context
        f_encoding = self.model.descriptor.encode
        (Pid, Pc, P)  = zip(*probeset.flatMap(lambda t: [(t.templateid(), t.category(), m) for m in t.media()])
                       .map(lambda (tid, tc, m): (tid, tc, f_encoding(m).flatten())).collect())
        (Gc, G) = zip(*[(k,x) for (k,v) in self.galleryset.iteritems() for x in v])
        (y, yhat, info) = self.model.testsvm(sparkContext=sc, probeset=(Pid, Pc, P), galleryset=(Gc, G), gallerysvms=self.gallerysvms, probesvms=probesvms)
        return (y, yhat, info)

    
    
