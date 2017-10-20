import os
import sys
import subprocess
import time
import dill as pickle # dill supports pickling lambdas
import argparse
import PIL
import numpy as np
import bobo.util
import cv2
from bobo.util import remkdir, islinux, ismacosx, timestamp
from bobo.image import ImageDetection
from bobo.cache import Cache
from janus.recognition import CompactAndDiscriminativeFaceTrackDescriptor
from janus.template import GalleryTemplate
from janus.gallery import Gallery_DS0
from janus.frontalize import frontalize_chip

# Parameters for caching and retrieving images
runstart = time.strftime('%Y%m%d-%H%M%S')
imageid = 0
cache = None

janus_error = {
        # No error
        'JANUS_SUCCESS'            : 0,
        # Catch-all error code
        'JANUS_UNKNOWN_ERROR'      : 1,
        # Memorry allocation failed
        'JANUS_OUT_OF_MEMORY'      : 2,
        # Incorrect location provided to janus_initialize
        'JANUS_INVALID_SDK_PATH'   : 3,
        # Failed to open a file
        'JANUS_OPEN_ERROR'         : 4,
        # Failed to read from a file
        'JANUS_READ_ERROR'         : 5,
        # Failed to write to a file
        'JANUS_WRITE_ERROR'        : 6,
        # Failed to parse file
        'JANUS_PARSE_ERROR'        : 7,
        # Could not decode image file
        'JANUS_INVALID_IMAGE'      : 8,
        # Could not decode video file
        'JANUS_INVALID_VIDEO'      : 9,
        # Expected a missing template ID
        'JANUS_MISSING_TEMPLATE_ID': 10,
        # Expected a missing file name
        'JANUS_MISSING_FILE_NAME'  : 11,
        # Null #janus_attribute_list
        'JANUS_NULL_ATTRIBUTE_LIST': 12,
        # Not all required attributes were provided
        'JANUS_MISSING_ATTRIBUTES' : 13,
        # Could not construct a template from the provided image andattributes
        'JANUS_FAILURE_TO_ENROLL'  : 14,
        # Optional functions may return in lieu of a meaninful implementation
        'JANUS_NOT_IMPLEMENTED'    : 15,
        'JANUS_NUM_ERRORS'         : 16,
        }


# janus_color_space = {
#         0: 'JANUS_GRAY8',
#         1: 'JANUS_BGR24',
#         }


class Evaluate(object):

    def __init__(self, sparkContext=None):
        self.sdk_path = None
        self.temp_path = None
        self.algorithm = None
        self.environ = None
        self.templates = []
        self.galleries = []
        self.sparkContext = sparkContext
        self.models = None
        self.args = None
        self.model = None
        self.frontalize = None
        self.gpu_idx = None

    # janus_train is not currently part of the Janus API, this is just a helper function for eval testing
    def janus_train(self, trainset, parameters=None):
        # preprocess images in template
        model = CompactAndDiscriminativeFaceTrackDescriptor()

        f_initialize = (lambda tmpl: tmpl.map(lambda im: model.preprocess(im)))
        trainset = trainset.map(lambda tmpl: f_initialize(tmpl))

        if parameters is not None:
            model = model.train(trainset,
                    gmmIterations=parameters['gmmIterations'],
                    trainingFeatures=parameters['trainingFeatures'],
                    svmIterations=parameters['svmterations'])
        else:
            model = model.train(trainset)

        self.model = model
        return self.model

    def janus_max_template_size(self):
        # Max template size is just about 1MB.  However, we want to amortize
        # the size of the models stored along with the templates in the
        # so max gallery size can be calculated. This comes out to about 3.2 MB
        size = 1024 * 1024 * 4
        print '[janus_max_template_size] %s: returning %d' % (timestamp(), size)
        return janus_error['JANUS_SUCCESS'], size

    """ janus_error janus_initialize(const char *sdk_path,
                                     const char *temp_path,
                                     const char *algorithm)
    """
    def janus_initialize(self, sdk_path, temp_path, algorithm):

        self.sdk_path  = sdk_path
        self.temp_path = temp_path
        self.algorithm = algorithm

        # Algorithm method will be used to select algorithm and parameters

        # The C interface will pass the 'algorithm' string as sys.argv
        parser = argparse.ArgumentParser(description='Janus face recognition parameters.')

        # E.g. /Volumes/janus_vol_0/jebyrne/fvfitw_19SEP14/vgg_gmm_pca_07OCT14.pyd
        parser.add_argument('--models')
        parser.add_argument('--debug', type=bool, default=False)
        parser.add_argument('--frontalize', type=bool, default=True)
        parser.add_argument('--gpu_idx', type=int, default=None)

        args = parser.parse_args(algorithm.split(';'))

        # Noblis scripts use algorithm string in filename when archiving results
        # May try URL encoding algorithm and decoding like this to make sure filename is valid:
        # import urllib
        # urllib.unquote(algorithm).decode('utf8') 

        if not args.models:
            print '[janus_initialize]: Model file path not specified in args: ', algorithm
            return janus_error['JANUS_MISSING_FILE_NAME']
        elif not os.path.exists(args.models):
            print '[janus_initialize]: Model file not found: ', args.models
            return janus_error['JANUS_MISSING_FILE_NAME']

        self.args = args

        self.debug = args.debug
        if self.debug:
            print '[janus_initialize]: Debug flag on'

        self.frontalize = args.frontalize
        self.gpu_idx = args.gpu_idx
        if self.frontalize is True and self.gpu_idx is None:
            print '[janus_initialize]: frontalize is True but gpu_idx not provided: ', algorithm
            return janus_error['JANUS_UNKNOWN_ERROR']
        elif self.frontalize is False and self.gpu_idx is not None:
            print '[janus_initialize]: Warning: gpu_idx provided, but frontalize is False. gpu_idx will be ignored: ', algorithm
        if self.frontalize is True:
            # Flush print statements to stdout to align w/ frontalization exe cout statements
            sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
            sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 0)

        # Don't load if we have models from janus_train
        if self.model is None:
            with open(self.args.models, 'r') as f:
                ref = pickle.load(f)
            self.model = CompactAndDiscriminativeFaceTrackDescriptor(gmm=copy.deepcopy(ref.gmm), pca=copy.deepcopy(ref.pca), metric=copy.deepcopy(ref.metric), do_weak_scale=False, do_random_jitter=False, do_color=False, do_weak_aspectratio=False)

        # Make sure we can find sdk path
        if sdk_path is None or not os.path.exists(sdk_path):
            print '[janus_initialize]: Path does not exist: %r' % sdk_path
            return janus_error['JANUS_INVALID_SDK_PATH']

        janus_env = os.path.join(sdk_path,'env.sh')
        if not os.path.exists(janus_env):
            print '[janus_initialize]: Cannot find env.sh in sdki_path: %r' % sdk_path
            return janus_error['JANUS_INVALID_SDK_PATH']

        command = ['bash', '-c', 'source %s && env'%janus_env]

        janus_env = subprocess.check_output(command)

        # JANUS_ROOT is sdk_path
        # JANUS_CACHE and JANUS_RESULTS are derived from temp_path
        # JANUS_DATA is only needed for unit testing
        envkeys = ['JANUS_ROOT', 'JANUS_RELEASE', 'JANUS_VENDOR', 'PATH',
                   'LD_LIBRARY_PATH', 'DYLD_FALLBACK_LIBRARY_PATH', 'PYTHONPATH']
        d = {key: value for (key,value) in [(v[0],v[1]) for v in
            [line.split('=',1) for line in iter(janus_env.splitlines())] if len(v)>1] if key in envkeys}

        missing_keys = [key for (key,has_key) in [(key,d.has_key(key)) for (key) in envkeys] if not has_key]

        # Sanity checks
        if not os.path.samefile(sdk_path, d['JANUS_ROOT']):
            print '[janus_initialize]: Error: sdk_path[%s] does not match JANUS_ROOT[%s]'%(sdk_path,d['JANUS_ROOT'])
            return janus_error['JANUS_INVALID_SDK_PATH']

        if len(missing_keys) > 1:
            print '[janus_initialize]: Error: not all expected environment variables were set by %s'%janus_env
            print '[janus_initialize]: ', missing_keys
            return janus_error['JANUS_INVALID_SDK_PATH']

        if len(missing_keys):
            if missing_keys[0] == 'LD_LIBRARY_PATH' and islinux():
                print '[janus_initialize]: Error: LD_LIBRARY_PATH was not set by %s'%janus_env
                return janus_error['JANUS_INVALID_SDK_PATH']
            if missing_keys[0] == 'DYLD_FALLBACK_LIBRARY_PATH' and ismacosx():
                print '[janus_initialize]: Error: DYLD_FALLBACK_LIBRARY_PATH was not set by %s'%janus_env
                return janus_error['JANUS_INVALID_SDK_PATH']

        # Make sure we can write to temp path
        if temp_path is None:
            print '[janus_initialize]: No temp_path was provided: temp_path: %r' % temp_path
            return janus_error['JANUS_INVALID_SDK_PATH']

        # Other variables
        # Set logs, results under temp path
        d['JANUS_LOGS'] = os.path.join(temp_path, 'logs', runstart)
        d['JANUS_DATA'] = os.path.join(temp_path, 'data')
        d['JANUS_CACHE'] = os.path.join(temp_path, 'cache')
        d['JANUS_RESULTS'] = os.path.join(temp_path, 'results')
        if islinux():
            d['JANUS_PLATFORM'] = 'centos7'
        else:
            d['JANUS_PLATFORM'] = 'macos10.9'

        try:
            remkdir(temp_path)
            remkdir(d['JANUS_LOGS'])
            remkdir(d['JANUS_CACHE'])
            remkdir(d['JANUS_RESULTS'])
        except:
            print '[janus_initialize]: Unable to create temp_path: %r' % temp_path
            return janus_error['JANUS_READ_ERROR']

        # Persist environment
        self.environ=d

        # Modify our environemnt
        for k,v in d.iteritems():
            os.environ[k] = v

        # Initialize cache key and image logging dir
        global cache
        cache = Cache()
        global logoutputdir
        logoutputdir = os.path.join(temp_path,'logs',runstart,'output')
        remkdir(logoutputdir)

        # Initialize Spark
        if self.sparkContext is None:
            sparkProperties = {
                    'spark.local.dir' : temp_path,
                    'spark.executor.memory': '2G',
                    }
            self.sparkContext = bobo.app.init('janus.evaluate', sparkProperties=sparkProperties)

        print '[janus_initialize] %s: Init success for sdk_path: [%s] and temp_path: [%s]'%(timestamp(), sdk_path, temp_path)
        return janus_error['JANUS_SUCCESS']


    """ janus_error janus_finalize()
    """
    def janus_finalize(self):
        print '[janus_finalize] %s' % (timestamp())
        return janus_error['JANUS_SUCCESS']


    """ janus_error janus_allocate_template(janus_template *template_)
    """
    def janus_allocate_template(self):
        template=GalleryTemplate()
        self.templates.append(template)
        print '[janus_allocate_template] %s' % (timestamp())
        return janus_error['JANUS_SUCCESS'],template


    """ janus_error janus_augment(const janus_image image,
                                  const janus_attribute_list attributes,
                                  janus_template template_)
    """
    def janus_augment(self, image, width, height, color_space, attribute_types, attribute_values, template):
        ## Generate a non-normalized FV for this image
        print '[janus_augment] %s: Begin' % (timestamp())
        if template not in self.templates:
            print '[janus_augment]: Template is not in my list:', template
            return janus_error['JANUS_UNKNOWN_ERROR']

        # print '[janus_augment]: DEBUG: image size=%d width=%d height=%d cs=%d' % (len(image), width, height, color_space)

        global imageid
        imageid += 1

        # Don't convert to grayscale here - let model preprocessing handle it
        data = np.array(PIL.Image.frombytes('RGB' if color_space is 1 else 'L',(width,height), image))

        # print '[janus_augment]: DEBUG: w=%d h=%d w*h=%d data.shape=%r' %(width, height, width*height, data.shape)

        imagefile = os.path.join(logoutputdir, '%08d.png' % imageid)

        # Strip off JANUS_ from attribute types to match bobo platform conventions
        atts = {k:v for (k,v) in [ (k[6:],v) for (k,v) in zip(attribute_types, attribute_values)]}

        xmin  =float(atts['FACE_X'])      if atts.has_key('FACE_X')      else float('nan')
        ymin  =float(atts['FACE_Y'])      if atts.has_key('FACE_Y')      else float('nan')
        width =float(atts['FACE_WIDTH'])  if atts.has_key('FACE_WIDTH')  else float('nan')
        height=float(atts['FACE_HEIGHT']) if atts.has_key('FACE_HEIGHT') else float('nan')
        atts['MEDIA_ID'] = imagefile

        # Create ImageDetection and pass to current template
        im = ImageDetection(url=cache.key(imagefile), category=None,
                xmin=xmin,
                ymin=ymin,
                xmax=xmin+width,
                ymax=ymin+height,
                attributes=atts)
        im.data = data

        if self.debug:
            rawimagefile = os.path.join(logoutputdir, '%08d_raw.png' % imageid)
            print '[janus_augment]: Writing raw image raw to %s'%rawimagefile
            cv2.imwrite(rawimagefile, data)

        if self.frontalize is True:
            cache_dir = bobo.app.logs()
            chip_dir = cache_dir + '/pvr/chips'
            remkdir(chip_dir)
            chip_path = os.path.join(chip_dir, '%08d.png' % imageid) 

            # Write chip to file for PVR
            # PVR will resample small images with width < 250
            im = im.crop(bbox=im.bbox.dilate(1.1)).resize(cols=300)
            print '[janus_augment]: Writing image chip to %s'%chip_path
            cv2.imwrite(chip_path, im.data.astype(np.uint8))

            try:
                frontalize_chip(chip_path, self.gpu_idx) 
                # Load frontlized chip from PVR output directory
                output_base_dir = cache_dir + '/pvr/frontalized'
                frontalized_dir = output_base_dir + '/frontalized'
                frontalized_chip_path = os.path.join(frontalized_dir, '%08d_frontalized_wsym.png' % imageid) 
                print '[janus_augment]: Reading frontalized chip from: %s'%frontalized_chip_path
                im.data = cv2.imread(frontalized_chip_path)
                print '[janus_augment]: Successfully read frontalized chip'
            except IOError:
                print '[janus_augment]: Failed to frontalize image.  Reverting to base version'
                im.data = data

        im = self.model.preprocess(im)

        template.augment(im)

        print '[janus_augment] %s: End' % (timestamp())
        return janus_error['JANUS_SUCCESS']


    """ janus_error janus_track(janus_template template_,
                                int enabled)
    """
    def janus_track(self, template, enabled):
        print '[janus_track]'
        return janus_error['JANUS_NOT_IMPLEMENTED']


    """ janus_error janus_free_template(janus_template template_)
    """
    def janus_free_template(self,template):
        print '[janus_free_template] %s' % (timestamp())
        self.templates.remove(template)
        return janus_error['JANUS_SUCCESS']


    """ janus_error janus_flatten_template(janus_template template_,
                                  janus_flat_template flat_template,
                                  size_t *bytes)
    """
    def janus_flatten_template(self, template):
        print '[janus_flatten_template] %s: Begin' % (timestamp())
        # Calculates FV
        template.flatten(self.model.f_encoding)
        # Pickle to buffer for later processing
        flat_template = pickle.dumps(template)
        print '[janus_flatten_template] %s: Returning template bytes: %d' % (timestamp(), len(flat_template))
        return janus_error['JANUS_SUCCESS'], flat_template


    """ janus_error janus_verify(const janus_flat_template a,
                                 const size_t a_bytes,
                                 const janus_flat_template b,
                                 const size_t b_bytes,
                                 float *similarity)

    """
    def janus_verify(self, flat_template_a, flat_template_b):
        print '[janus_verify] %s: Begin' % (timestamp())
        a = pickle.loads(flat_template_a)
        b = pickle.loads(flat_template_b)

        probeset = self.sparkContext.parallelize([a])
        galleryset = self.sparkContext.parallelize([b])

        (y,yhat,info) = Gallery_DS0(self.model).test(probeset, galleryset)
        similarity = yhat[0]

        print '[janus_verify] %s: Returning similarity: %f' % (timestamp(), similarity)
        return janus_error['JANUS_SUCCESS'], similarity


    """ janus_error janus_enroll(const janus_template template_,
                                 const janus_template_id template_id,
                                 janus_gallery gallery)

    """
    def janus_enroll(self, template, template_id, gallery):
        print '[janus_enroll] %s: Begin' % (timestamp())
        gallery.enroll_template(template, template_id=template_id)
        print '[janus_enroll] %s: End' % (timestamp())
        return janus_error['JANUS_SUCCESS']


    """ janus_error janus_allocate_gallery(janus_gallery *gallery)
    """
    def janus_allocate_gallery(self):
        print '[janus_allocate_gallery] %s: Begin' % (timestamp())
        gallery=Gallery_DS0(self.model)
        self.galleries.append(gallery)
        print '[janus_allocate_gallery] %s: End' % (timestamp())
        return janus_error['JANUS_SUCCESS'],gallery


    """ janus_error janus_free_gallery(janus_gallery gallery)
    """
    def janus_free_gallery(self, gallery):
        print '[janus_free_gallery] %s' % (timestamp())
        self.galleries.remove(gallery)
        return janus_error['JANUS_SUCCESS']


    """ janus_error janus_flatten_gallery(const janus_gallery gallery,
                                          janus_flat_gallery flat_gallery,
                                          size_t *bytes)

    """
    def janus_flatten_gallery(self, gallery):
        print '[janus_flatten_gallery] %s: Begin' % (timestamp())
        # Pickle to buffer for later processing
        templates = self.sparkContext.parallelize( gallery.templates.iteritems() )
        flat_templates = gallery.flatten_templates(templates)
        gallery.templates = flat_templates
        # for (i, t) in gallery.templates.iteritems():
        #     print '[janus_flatten_gallery]: Debug: tid:%s, category:%s, len_fv:%r, len_media:%r' % (i, t.category, 'None' if t.fishervector is None else len(t.fishervector), 'None' if t.media is None else len(t.media) )
        flat_gallery = pickle.dumps(gallery)
        print '[janus_flatten_gallery] %s: End' % (timestamp())
        return janus_error['JANUS_SUCCESS'], flat_gallery


    """ janus_error janus_search(const janus_template template_,
                                 janus_gallery gallery,
                                 int requested_returns,
                                 janus_template_id *template_ids,
                                 float *similarities,
                                 int *actual_returns)
    """
    def janus_search(self, flat_template, flat_gallery, requested_returns):
        print '[janus_search] %s: Requested returns: %d' % (timestamp(), requested_returns)
        probe = pickle.loads(flat_template)
        gallery = pickle.loads(flat_gallery)

        probegallery = Gallery_DS0(self.model)
        probegallery.enroll_template(probe, 'PROBE_X')

        probeset = self.sparkContext.parallelize( probegallery.templates.values() )
        galleryset = self.sparkContext.parallelize( gallery.templates.values() )

        (y,yhat,info) = gallery.test(probeset, galleryset)
        results = zip(yhat, gallery.templates.keys())
        sorted_results = sorted(results, reverse=True)
        returns = sorted_results[0:requested_returns]
        sims, tids = zip(*returns)
        print '[janus_search] %s: Actual sims: %d, actual tids: %d:' % (timestamp(), len(sims), len(tids))

        return janus_error['JANUS_SUCCESS'], tids, sims, len(sims)

