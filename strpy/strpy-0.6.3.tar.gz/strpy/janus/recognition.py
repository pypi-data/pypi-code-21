import os
import strpy.bobo.metrics
#import bobo.util
import strpy.janus.gmm
import strpy.janus.features
from strpy.janus.features import densesift, densePCAsift, denseMultiscaleSIFT, denseMultiscaleColorSIFT
import strpy.janus.encoding
from strpy.janus.encoding import fishervector, fishervector_pooling, augment_fishervector
import strpy.janus.reduction
import numpy as np
from strpy.bobo.classification import linearsvm
from strpy.bobo.util import quietprint, seq, tolist, tempjpg, load, save, timestamp, Stopwatch, fileext, islist, remkdir, imread, isstring, mktemp, writecsv, filebase
from strpy.janus.openbr import readbinary
import sklearn.decomposition
#from pyspark.mllib.classification import SVMWithSGD
#from pyspark.mllib.regression import LabeledPoint
from itertools import product as cartesian
from itertools import combinations
import pdb
import math
from strpy.janus.cache import root as cacheDir
import strpy.janus.classifier
from strpy.janus.classifier import DiscriminativeDimensionalityReduction  # must include for pickle file backwards compatibility!
from strpy.janus.classifier import LinearSVMGalleryAdaptation
from strpy.janus.frontalize import frontalize_face_v5, FrontalizerFaceV5
from glob import glob
from strpy.bobo.geometry import BoundingBox, normalize, sqdist
from strpy.janus.template import GalleryTemplate
import strpy.bobo.linalg
from strpy.janus.detection import DlibObjectDetector
from strpy.bobo.video import VideoDetection
import strpy.janus.environ

class CompactAndDiscriminativeFaceTrackDescriptor():
    def __init__(self, gmm=None, pca=None, metric=None, do_weak_scale=False, do_random_jitter=False, do_color=False, do_weak_aspectratio=False, do_jitter=True, gausshape=None, scales=[1.0, 1.0/np.sqrt(2), 0.5, 1.0/(2*np.sqrt(2)), 0.25]):
        # Model parameters
        self.pca = pca
        self.gmm = gmm
        self.metric = metric
        self.do_weak_scale = do_weak_scale
        self.do_random_jitter=do_random_jitter
        self.flat_probeset = None
        self.flat_galleryset = None
        self.do_color = do_color
        self.do_weak_aspectratio = do_weak_aspectratio
        self.do_jitter = do_jitter
        self.gausshape = gausshape

        scales = tolist(scales)

        # Dense SIFT
        if do_color is False:
            self.f_densesift = (lambda im: denseMultiscaleSIFT(im, scales=scales, dx=1, dy=1, weakGeometry=True, rootsift=True, binSizeX=6, binSizeY=6, floatDescriptor=False, do_fast=False, do_weak_scale=do_weak_scale, weakAspectRatio=do_weak_aspectratio))
        else:
            self.f_densesift = (lambda im: denseMultiscaleColorSIFT(im, scales=scales, dx=1, dy=1, weakGeometry=True, rootsift=True, binSizeX=6, binSizeY=6, floatDescriptor=False, do_fast=False, weakAspectRatio=do_weak_aspectratio))

        # Weak geometry
        if self.do_weak_scale or self.do_weak_aspectratio:
            self.f_densesift_only = (lambda d: d[0:-3])  # remove weak geometry from descriptor (final three columns)
            self.f_pcasift = (lambda d: reduce(lambda x,y: np.concatenate( (self.pca.transform(x).flatten(),y) ), np.split(d, [len(d)-3])))
            self.f_densePCAsift = (lambda im: reduce(lambda x,y: np.concatenate( (self.pca.transform(x),y), axis=1), np.split(self.f_densesift(im), [-3], axis=1)))
        else:
            self.f_densesift_only = (lambda d: d[0:-2])  # remove weak geometry from descriptor (final two columns)
            self.f_pcasift = (lambda d: reduce(lambda x,y: np.concatenate( (self.pca.transform(x).flatten(),y) ), np.split(d, [len(d)-2])))
            self.f_densePCAsift = (lambda im: reduce(lambda x,y: np.concatenate( (self.pca.transform(x),y), axis=1), np.split(self.f_densesift(im), [-2], axis=1)))

        # Fisher vector encoding
        if self.gausshape is not None:
            self.f_fishervector = (lambda im: fishervector(im, features=self.f_densePCAsift, gmm=self.gausshape.posterior(im, self.gmm, features=self.f_densePCAsift(im)[::4, :]), do_improvedfisher=False, do_fastfisher=False))
        else:
            self.f_fishervector = (lambda im: fishervector(im, features=self.f_densePCAsift, gmm=self.gmm, do_improvedfisher=False, do_fastfisher=False))

        # Media pooling
        self.f_encoding = (lambda t: fishervector_pooling(t, f_encoding=self.f_fishervector, do_jitter=self.do_jitter, do_signsqrt=True, do_normalized=True, do_verbose=True, do_random_jitter=self.do_random_jitter))

    def f_preprocess(self):
        if self.do_color:
            return lambda im: im.float(1.0/255.0).crop(bbox=im.bbox.dilate(1.1)).resize(rows=150)
        else:
            return lambda im: im.preprocess().crop(bbox=im.bbox.dilate(1.1)).resize(rows=150)

    def preprocess(self, im):
        return self.f_preprocess()(im)

    def encode(self, im):
        return self.f_encoding(im)

    def train(self, trainset, gmmModes=512, pcaComponents=64, gmmIterations=20, do_ddr=True, do_jointmetric=True, do_parallel_sgd=False, seed=42, trainingFeatures=1E6, svmIterations=1E6, numBatches=1E2, do_metric=True, dimReduce=128, pairs=None, bias_retrain_fraction=0.0):
        quietprint('[janus.recognition]: "A Compact and Discriminative Face Track Descriptor" ', verbosity=1)
        np.random.seed(int(seed))

        # Feature set: randomly sample features from images in templates in trainset
        featset = trainset.flatMap(lambda tmpl: tolist(tmpl.images())+tolist(tmpl.frames())) # templates to images
        featset = featset.flatMap(self.f_densesift) # explode descriptors into RDD of features

        # PCA dimensionality reduction on dense sift only, then augment with weak geometry
        if self.pca is None:
            quietprint('[janus.recognition][ACaDFTD.train]: "PCA" ', verbosity=1)
            pcaset = featset.context.parallelize(featset.map(self.f_densesift_only).takeSample(withReplacement=False, num=int(trainingFeatures), seed=int(seed)))
            self.pca = janus.reduction.pca(pcaset, n_components=pcaComponents)

        # GMM learning
        if self.gmm is None:
            quietprint('[janus.recognition][ACaDFTD.train]: "GMM learning" ', verbosity=1)
            gmmset = featset.context.parallelize(featset.map(self.f_pcasift).takeSample(withReplacement=False, num=int(trainingFeatures), seed=int(seed)))
            self.gmm = janus.gmm.train(gmmset, n_modes=gmmModes, do_verbose=True, n_iterations=gmmIterations, seed=int(seed))

        # Metric learning
        if bias_retrain_fraction > 0.0 and pairs is not None:
            pairs, pairs_bias = pairs.randomSplit([1.0-bias_retrain_fraction, bias_retrain_fraction], seed=seed)
        elif bias_retrain_fraction < 0.0 and pairs is not None:
            pairs_bias = pairs.sample(withReplacement=False, fraction=-bias_retrain_fraction, seed=seed)
        else:
            pairs_bias = None
        mediaset = trainset.flatMap(lambda tmpl: tmpl.images()+tmpl.videos()) # templates to media
        encodedset = mediaset.map(lambda t: (t.category(), self.f_encoding(t).flatten()))
        if self.metric is None and do_metric is True:
            quietprint('[janus.recognition][ACaDFTD.train]: "Metric learning" ', verbosity=1)
            #quietprint('%i %i'%(trainset.count(), mediaset.count()))
            if do_ddr:
                metric = janus.classifier.DiscriminativeDimensionalityReduction(seed=seed, do_jointmetric=do_jointmetric)
                if do_parallel_sgd:
                    self.metric = metric.train_parallel(encodedset, numIterations=svmIterations, dimReduce=dimReduce, gamma=0.25, gammaBias=10, numBatches=numBatches, pairs=pairs)
                else:
                    self.metric = metric.train(encodedset, numIterations=svmIterations, dimReduce=dimReduce, gamma=0.25, gammaBias=10, pairs=pairs, numPca=pairs.count(), numBiasTrain=0)
            else:
                metric = janus.classifier.RankingSVM();
                self.metric = metric.train(mediaset, numIterations=svmIterations, f_unary=self.f_encoding, pairs=pairs)

        # Fix bias
        if self.metric is not None and bias_retrain_fraction != 0.0:
            self.metric.train_bias(encodedset, pairs_bias)

        # Output
        return self


    def test(self, probeset=None, galleryset=None, with_templateid=False, with_labels=False):
        if (self.pca is None or self.gmm is None or self.metric is None):
            raise ValueError('Untrained model')

        # Test if templates have been flattened
        f_encoding = self.f_encoding  # avoid large closure
        f_flatten = (lambda t: t._fishervector if t._is_flattened else f_encoding(t))
        # test_flattened takes a list of tuples of (templateID, category, feature)

        if probeset is not None:
            P = probeset.map(lambda t: (t.templateid(), t.category(), f_flatten(t).flatten()))
            self.flat_probeset = P.collect()
            #flat_probeset = P.collect()   # FIXME: avoid large closure, do not store flat gallery as attribute

        if galleryset is not None:
            G = galleryset.map(lambda t: (t.templateid(), t.category(), f_flatten(t).flatten()))
            self.flat_galleryset = G.collect()
            #flat_galleryset = G.collect()  # FIXME: avoid large closure, do not store flat gallery as attribute

        if self.flat_probeset is None or self.flat_galleryset is None:
            raise ValueError('Probeset[%s] and galleryset[%s] are required!' % (str(self.flat_probeset), str(self.flat_galleryset)))

        (y, yhat, info) = self.metric.test_flattened(probeset=self.flat_probeset, galleryset=self.flat_galleryset)

        # Output tuple formatting
        if with_templateid and with_labels:
            results = (y, yhat, info['templateIDpairs'], info['labelpairs'])
        elif with_templateid:
            results = (y, yhat, info['templateIDpairs'])
        elif with_labels:
            results = (y, yhat, info['labelpairs'])
        else:
            results = (y, yhat)

        return results


    def testfast(self, probeset, galleryset, isencoded=False):
        """Precompute Wx and Vx distributed for fast similarity matrix construction using probeset/galleryset RDD"""
        if (self.pca is None or self.gmm is None or self.metric is None):
            raise ValueError('Untrained model')

        # Precompute metrics
        f_encoding = self.f_encoding  # avoid large closure?
        W = self.metric.model['W']
        V = self.metric.model['V']
        b = self.metric.model['b']

        if isencoded == False:
            probeset = probeset.map(lambda t: (t.templateid(), t.category(), f_encoding(t).flatten()))
            galleryset = galleryset.map(lambda t: (t.templateid(), t.category(), f_encoding(t).flatten()))

        fast_probeset = probeset.map(lambda (tid,c,x): (tid, c, (W.dot(x)), (V.dot(x)) if V is not None else None)).collect()
        fast_galleryset = galleryset.map(lambda (tid,c,x): (tid, c, (W.dot(x)), (V.dot(x)) if V is not None else None)).collect()

        if isencoded == False:
            # If user is handling encoding, let them handle persistence as well
            probeset.unpersist()
            galleryset.unpersist()

        # Fast distance
        y=[]; yhat=[]; templateIDpairs=[]; labelpairs=[]
        for (pid, pc, pw, pv) in fast_probeset:
            for (qid, qc, qw, qv) in fast_galleryset:
                if self.metric.do_jointmetric is True and pv is not None and qv is not None:
                    yhat.append(float(b - (0.5 * np.sum(np.square(pw-qw)) - pv.dot(qv))))
                else:
                    yhat.append(float(b - (0.5 * np.sum(np.square(pw-qw)))))
                y.append(float(pc == qc))
                templateIDpairs.append( (pid, qid) )
                labelpairs.append( (pc, qc) )

        return (y, yhat, {'templateIDpairs':templateIDpairs, 'labelpairs':labelpairs})

    def testfastpairs(self, rdd, pairs, isencoded=False):
        """Similar to testfast(), but test specific pairs rather than all pairs"""

        if (self.pca is None or self.gmm is None or self.metric is None):
            raise ValueError('Untrained model')

        # Precompute metrics
        f_encoding = self.f_encoding  # avoid large closure?
        W = self.metric.model['W']
        V = self.metric.model['V']
        b = self.metric.model['b']

        if isencoded == False:
            rdd = rdd.map(lambda t: (t.templateid(), t.category(), f_encoding(t).flatten()))

        do_jointmetric = self.metric.do_jointmetric and V is not None
        if do_jointmetric:
            data = rdd.map(lambda (tid,c,x): (tid, c, (W.dot(x)), (V.dot(x)))).collect()
            def compute(i,j,y):
                pid,pc,pw,pv = data[i]
                qid,qc,qw,qv = data[j]
                assert (pc==qc) == y
                return (
                    float(pc==qc),                                                  # y
                    (float(b - (0.5 * np.sum(np.square(pw-qw)) - pv.dot(qv)))),     # yhat
                    (pid, qid),                                                     # template IDs
                    (pc, qc))                                                       # categories
        else:
            data = rdd.map(lambda (tid,c,x): (tid, c, (W.dot(x)))).collect()
            def compute(i,j,y):
                pid,pc,pw = data[i]
                qid,qc,qw = data[j]
                assert (pc==qc) == y
                return (
                    float(pc==qc),                                                  # y
                    (float(b - (0.5 * np.sum(np.square(pw-qw))))),                  # yhat
                    (pid, qid),                                                     # template IDs
                    (pc, qc))                                                       # categories
        pairs = pairs.map(lambda (i,j,y): compute(i,j,y))

        y, yhat, templateIDpairs, labelpairs = zip(*pairs.collect())
        return y, yhat, {'templateIDpairs':templateIDpairs, 'labelpairs':labelpairs}

    def identify(self, probe, galleryset, is_gallery_encoded=False):
        """Test a probe template against a set of gallery templates"""
        if (self.pca is None or self.gmm is None or self.metric is None):
            raise ValueError('Untrained model')

        # Precompute metrics
        f_encoding = self.f_encoding
        W = self.metric.model['W']
        V = self.metric.model['V']
        b = self.metric.model['b']

        f_fastreduce = lambda (tid,c,x): (tid, c, (W.dot(x)), (V.dot(x)) if V is not None else None)

        if isinstance(probe, GalleryTemplate): # Else, assume probe is already a (templateid, category, feature vector) tuple
            probe = (probe.templateid(), probe.category(), f_encoding(probe).flatten())

        (pid, pc, pw, pv) = f_fastreduce(probe)

        if is_gallery_encoded == False:
            galleryset = galleryset.map(lambda t: (t.templateid(), t.category(), f_encoding(t).flatten()))
            fast_galleryset = galleryset.map(f_fastreduce).collect()
            galleryset.unpersist()
        else:
            fast_galleryset = [f_fastreduce(g) for g in galleryset]

        # Fast distance
        y=[]; yhat=[]; templateIDpairs=[]; labelpairs=[]
        for (qid, qc, qw, qv) in fast_galleryset:
            if self.metric.do_jointmetric is True and pv is not None and qv is not None:
                yhat.append(float(b - (0.5 * np.sum(np.square(pw-qw)) - pv.dot(qv))))
            else:
                yhat.append(float(b - (0.5 * np.sum(np.square(pw-qw)))))
            y.append(float(pc == qc))
            templateIDpairs.append( (pid, qid) )
            labelpairs.append( (pc, qc) )

        return (y, yhat, {'templateIDpairs':templateIDpairs, 'labelpairs':labelpairs})


    def augment_gallery(self, galleryset, rdd=True):
        # Test if templates have been flattened
        f_encoding = self.f_encoding
        f_flatten = (lambda t: t.fishervector if t._is_flattened else f_encoding(t))
        if rdd == True:
            G = galleryset.map(lambda t: (t.templateid(), t.category(), f_flatten(t).flatten())).collect()
        else:
            G = [(t.templateid(), t.category(), f_flatten(t).flatten()) for t in galleryset]

        # FIXME: Merging normalized fishervectors is not valid
        # Merge templates already in flat_galleryset with the same template id, preserving template order.
        # Assumes no duplicate template ids in the galleryset parameter (OK if already in flat_gallery).
        # flat_galleryset lookup: template_id:feature
        if self.flat_galleryset is None:
            self.flat_galleryset = []
        galdict = {t[0]:t[2] for t in self.flat_galleryset}
        for (tmplid, label, fv) in G:
            if tmplid not in galdict:
                self.flat_galleryset.append((tmplid, label, fv))
            else:
                fv = augment_fishervector(galdict[tmplid], fv)
                #FIXME: This could get slow for very large galleries
                for (k, t) in enumerate(self.flat_galleryset):
                    if t[0] == tmplid:
                        self.flat_galleryset[k] = (tmplid, label, fv)
                        break

        return self

    def similarity(self, imp, imq):
        """Compute similarity between two images"""
        return self.metric.similarity(self.f_encoding(imp).flatten(), self.f_encoding(imq).flatten())


    def fishervectors(self, imset):
        """Return (im,x) tuples for image object im and fisher vector x"""
        f_encoding = self.f_encoding
        return imset.map(lambda im: (im, f_encoding(im)))

    def discriminativeFeatures(self, imset):
        """Return (im, f) tuples for image im and low dimensional discriminative features f"""
        f_encoding = self.f_encoding
        f_projection = self.metric.projection
        return imset.map(lambda im: (im, f_projection(f_encoding(im))))



class MultiScaleGmmDescriptor(object):
    def __init__(self, scales=[1.0, 1.0/np.sqrt(2), 0.5, 1.0/(2*np.sqrt(2)), 0.25], clusters=[256, 138, 70, 38, 10], metric=None, do_weak_scale=False, do_random_jitter=False, do_color=False, do_weak_aspectratio=False, do_jitter=True, gausshape=None):
        self.scales = scales
        self.clusters = clusters
        self.models = []
        self.encodings = []
        self.metric = metric
        self.do_weak_scale = do_weak_scale
        self.do_random_jitter=do_random_jitter
        self.do_color = do_color
        self.do_weak_aspectratio = do_weak_aspectratio
        self.do_jitter = do_jitter
        self.gausshape = gausshape

    def train(self, trainset, pcaComponents=64, gmmIterations=20, trainingFeatures=1E6, seed=42, do_metric=True, do_ddr=True, do_parallel_sgd=True, numIterations=1E6, numBatches=1E2, do_jointmetric=True, dimReduce=128, warmstart=False):
        # FIXME: Warmstart, scale augment?
        quietprint('[janus.recognition.multiscalegmm]: Debug: warmstart=%r, scales=%d, models=%d'%(warmstart, len(self.scales), len(self.models)))
        if warmstart and len(self.models) == len(self.scales):
            quietprint('[janus.recognition.multiscalegmm]: Using existing models')
        else:
            self.models = []
            for k, scale in enumerate(self.scales):
                quietprint('[janus.recognition.multiscalegmm] %s: Training [%d/%d]'%(timestamp(), k+1, len(self.scales)))
                model = CompactAndDiscriminativeFaceTrackDescriptor(scales=[scale], do_weak_scale=self.do_weak_scale, do_random_jitter=self.do_random_jitter, do_color=self.do_color, do_weak_aspectratio=self.do_weak_aspectratio, do_jitter=self.do_jitter, gausshape=self.gausshape)
                gmmModes = self.clusters[k]
                with Stopwatch() as sw:
                    model = model.train(trainset, gmmModes=gmmModes, pcaComponents=pcaComponents, gmmIterations=gmmIterations, seed=seed, trainingFeatures=trainingFeatures, do_metric=False)
                quietprint('[janus.recognition.multiscalegmm] %s: Training [%d/%d] complete in %.1fs'%(timestamp(), k+1, len(self.scales), sw.elapsed))
                self.models.append(model)

        self.f_encoding = (lambda t: np.concatenate([m.f_encoding(t) for m in self.models], 1))

        def encoding(tmpl):
            try:
                return self.f_encoding(tmpl)
            except:
                print 'tmpl error: %r' % tmpl
                raise

        f_encoding = encoding

        # Metric learning
        if self.metric is None and do_metric is True:
            mediaset = trainset.flatMap(lambda tmpl: tmpl.images()+tmpl.videos()) # templates to media
            if do_ddr:
                metric = janus.classifier.DiscriminativeDimensionalityReduction(seed=seed, do_jointmetric=do_jointmetric)
                if do_parallel_sgd:
                    self.metric = metric.train_parallel(mediaset.map(lambda t: (t.category(), f_encoding(t).flatten())), numIterations=numIterations, dimReduce=dimReduce, gamma=0.25, gammaBias=10, numBatches=numBatches)
                else:
                    self.metric = metric.train(mediaset, numIterations=numIterations, f_unary=f_encoding, dimReduce=dimReduce, gamma=0.25, gammaBias=10)
            else:
                metric = janus.classifier.RankingSVM();
                self.metric = metric.train(mediaset, numIterations=numIterations, f_unary=f_encoding)
        return self

    def testfast(self, probeset, galleryset):
        """Precompute Wx and Vx distributed for fast similarity matrix construction using probeset/galleryset RDD"""
        if (len(self.models) < 1 or self.metric is None):
            raise ValueError('Untrained model')

        # Precompute metrics
        f_encoding = self.f_encoding  # avoid large closure?
        W = self.metric.model['W']
        V = self.metric.model['V']
        b = self.metric.model['b']

        fast_probeset = probeset.map(lambda t: (t.templateid(), t.category(), f_encoding(t).flatten())).map(lambda (tid,c,x): (tid, c, (W.dot(x)), (V.dot(x)) if V is not None else None)).collect()
        fast_galleryset = galleryset.map(lambda t: (t.templateid(), t.category(), f_encoding(t).flatten())).map(lambda (tid,c,x): (tid, c, (W.dot(x)), (V.dot(x)) if V is not None else None)).collect()

        # Fast distance
        y=[]; yhat=[]; templateIDpairs=[]; labelpairs=[]
        for (pid, pc, pw, pv) in fast_probeset:
            for (qid, qc, qw, qv) in fast_galleryset:
                if self.metric.do_jointmetric is True and pv is not None and qv is not None:
                    yhat.append(float(b - (0.5 * np.sum(np.square(pw-qw)) - pv.dot(qv))))
                else:
                    yhat.append(float(b - (0.5 * np.sum(np.square(pw-qw)))))
                y.append(float(pc == qc))
                templateIDpairs.append( (pid, qid) )
                labelpairs.append( (pc, qc) )

        return (y, yhat, {'templateIDpairs':templateIDpairs, 'labelpairs':labelpairs})




def a_compact_and_discriminative_face_track_descriptor(trainset, galleryset, probeset, pca=None, gmm=None, model=None, gmmModes=512, pcaComponents=64, gmmIterations=20, trainingFeatures=1E6, seed=42, svmIterations=1E6, svmBatchFraction=1.0, do_ddr=True, do_parallel_sgd=False, do_mediatraining=True, numBiasTrain=1E3):
    """A Compact and Discriminnative Face Track Descriptor, CVPR'14"""
    quietprint('[janus.recognition]: "A Compact and Discriminative Face Track Descriptor" ')
    np.random.seed(seed)

    # Dense SIFT:
    f_densesift = (lambda im: denseMultiscaleSIFT(im, scales=[1.0, 1.0/np.sqrt(2), 0.5, 1.0/(2*np.sqrt(2)), 0.25], dx=1, dy=1, weakGeometry=True, rootsift=True, binSizeX=6, binSizeY=6, floatDescriptor=False, do_fast=False))
    #f_densesift = janus.cache.preserve(f_densesift) if memoize else janus.cache.flush(f_densesift)
    f_densesift_only = (lambda d: d[0:-2])  # remove weak geometry from descriptor (final two columns)

    # Feature set: randomly sample features from images in templates in trainset
    featset = trainset.flatMap(lambda tmpl: tolist(tmpl.images())+tolist(tmpl.frames())) # templates to images
    #n_featuresPerImage = np.ceil(float(trainingFeatures) / float(featset.count()))
    featset = featset.flatMap(f_densesift) # explode descriptors into RDD of features

    # PCA dimensionality reduction on dense sift only, then augment with weak geometry
    if pca is None:
        pcaset = featset.context.parallelize(featset.map(f_densesift_only).takeSample(withReplacement=False, num=int(trainingFeatures), seed=int(seed)))
        pca = janus.reduction.pca(pcaset, n_components=pcaComponents)
    f_pcasift = (lambda d: reduce(lambda x,y: np.concatenate( (pca.transform(x).flatten(),y) ), np.split(d, [128])))

    # GMM learning
    if gmm is None:
        gmmset = featset.context.parallelize(featset.map(f_pcasift).takeSample(withReplacement=False, num=int(trainingFeatures), seed=int(seed)))
        gmm = janus.gmm.train(gmmset, n_modes=gmmModes, do_verbose=True, n_iterations=gmmIterations, seed=int(seed))

    # Fisher vector encoding
    f_densePCAsift = (lambda im: reduce(lambda x,y: np.concatenate( (pca.transform(x),y), axis=1), np.split(f_densesift(im), [128], axis=1)))
    f_fishervector = (lambda im: fishervector(im, features=f_densePCAsift, gmm=gmm, do_improvedfisher=False, do_fastfisher=False))
    f_encoding = (lambda t: fishervector_pooling(t, f_encoding=f_fishervector, do_jitter=True, do_signsqrt=True, do_normalized=True, do_verbose=True))

    # Model training
    if model is None:
        mediaset = trainset.flatMap(lambda tmpl: tmpl.images()+tmpl.videos()) # templates to list of media, do_mediatraining=True
        if do_ddr:
            model = janus.classifier.DiscriminativeDimensionalityReduction(seed=seed, do_jointmetric=True)
            if do_parallel_sgd:
                model = model.train_parallel(mediaset.map(lambda x: (x.category(), f_encoding(x).flatten())), numIterations=svmIterations, dimReduce=128, gamma=0.25, gammaBias=10, numBiasTrain=numBiasTrain)
            else:
                model = model.train(mediaset, numIterations=svmIterations, f_unary=f_encoding, dimReduce=128, gamma=0.25, gammaBias=10)
        else:
            model = janus.classifier.RankingSVM();
            model = model.train(mediaset, numIterations=svmIterations, f_unary=f_encoding)

    # Model evaluation
    (y, yhat, tid) = model.test(probeset, galleryset, f_unary=f_encoding)

    # Output
    prms = {'model':model, 'gmm':gmm, 'pca':pca, 'probe_gallery_template_ids':tid}
    return ((y, yhat), prms)


def fisher_vector_faces_in_the_wild(trainset, testset, visualwords=None, f_pca=None, n_modes=512, trainingFeatures=1E6, seed=42, gmmIterations=20, mirroredTesting=True, memoize=False):
    """Face Verification using 'fisher vector faces in the wild', BMVC 2013"""
    # http://www.robots.ox.ac.uk/~vedaldi/assets/pubs/simonyan13fisher.pdf

    # Initialization
    np.random.seed(seed)

    # Dense SIFT
    f_densesift = (lambda im: denseMultiscaleSIFT(im, scales=[1.0, 1.0/np.sqrt(2), 0.5, 1.0/(2*np.sqrt(2)), 0.25], dx=1, dy=1, weakGeometry=True, rootsift=True, binSizeX=6, binSizeY=6, floatDescriptor=False, do_fast=True))
    #f_densesift = janus.cache.preserve(f_densesift) if memoize else janus.cache.flush(f_densesift)
    f_densesift_only = (lambda d: d[0:-2])  # remove weak geometry from descriptor (final two columns)

    # Feature set: randomly sample features from each pair of images in training set
    #n_featuresPerImage = np.ceil(float(trainingFeatures) / float(2*trainset.count()))
    featset = (trainset.flatMap(lambda impair: impair) # explode RDD of images from (improbe, imgallery) tuples
               .flatMap(f_densesift)) # feature extraction within bounding box
                        #.flatMap(lambda x: rng.permutation(x)[0:np.minimum(n_featuresPerImage,x.shape[0]),:])) # random selection of k descriptors per image and explode into RDD of features

    # PCA dimensionality reduction on dense sift only, then augment with weak geometry
    if f_pca is None:
        pcaset = featset.context.parallelize(featset.map(f_densesift_only).takeSample(withReplacement=False, num=int(trainingFeatures), seed=int(seed)))
        pca = janus.reduction.pca(pcaset, n_components=64)
        f_pca = pca.transform
    else:
        pca = None
    f_pcasift = (lambda d: reduce(lambda x,y: np.concatenate( (f_pca(x).flatten(),y) ), np.split(d, [128])))

    # GMM learning
    if visualwords is None:
        gmmset = featset.context.parallelize(featset.map(f_pcasift).takeSample(withReplacement=False, num=int(trainingFeatures), seed=int(seed)))
        visualwords = janus.gmm.train(gmmset, n_modes=n_modes, do_verbose=True, n_iterations=gmmIterations, seed=int(seed))

    # Fisher vector encoding
    f_densePCAsift = (lambda im: reduce(lambda x,y: np.concatenate( (f_pca(x),y), axis=1), np.split(f_densesift(im), [128], axis=1)))
    f_encoding = (lambda im: fishervector(im, features=f_densePCAsift, gmm=visualwords, do_signsqrt=True, do_normalized=True, do_improvedfisher=True, do_fastfisher=False))
    f_fishervector = (lambda (improbe, imgallery): np.square(f_encoding(improbe) - f_encoding(imgallery)))

    # Structured Ranking SVM
    svm = janus.classifier.StructuredSVMForRanking(features=f_fishervector).train(trainset, svmLambda=1E-8, batchFraction=0.15)  # Structured SVM for ranking (section 4.3)

    # Testing
    if mirroredTesting:
        f_mirror = (lambda im: im.fliplr())
        (y, yhata) = svm.test(testset.map(lambda (imp, imq): (imp, imq)))
        (y, yhatb) = svm.test(testset.map(lambda (imp, imq): (imp, f_mirror(imq))))
        (y, yhatc) = svm.test(testset.map(lambda (imp, imq): (f_mirror(imp), f_mirror(imq))))
        (y, yhatd) = svm.test(testset.map(lambda (imp, imq): (f_mirror(imp), imq)))
        yhat = np.mean(np.array([yhata, yhatb, yhatc, yhatd]), axis=0)
    else:
        (y, yhat) = svm.test(testset)

    # Garbage collection
    trainset = trainset.unpersist()
    testset = testset.unpersist()
    featset = featset.unpersist()

    # Output
    model = {'svm':svm.model, 'visualwords':visualwords, 'pca':pca}  # FIXME: can't pickle model?
    return ((y, yhat), model)


def bagofvisualwords(trainset, testset, n_modes=4, seed=None):
    """Classic bag-of-words encoding for verification"""
    f_improbe = (lambda (improbe, imgallery): improbe)  # return only probe image, ignore gallery image from input tuple
    f_densesift = (lambda im: densesift(im, dx=4, dy=4, weakGeometry=True, rootsift=True))
    visualwords = janus.gmm.jebyrne_train(trainset.map(f_improbe), features=f_densesift, fractionOfImages=0.1, fractionOfDescriptors=0.1, n_modes=n_modes)
    f_bagofwords = (lambda (improbe, imgallery): np.square(janus.encoding.bagofwords(improbe, features=f_densesift, gmm=visualwords)
                                                           - janus.encoding.bagofwords(imgallery, features=f_densesift, gmm=visualwords)))

    model = janus.classifier.Verification(binaryclassifier=linearsvm, features=f_bagofwords)  # linear SVM verification classifier with fisher vector features
    (y, yhat) = model.train(trainset).test(testset)  # Diagonal metric learning: section 4.3
    return ((y, yhat), {'visualwords':visualwords})


class RecognitionD0_1(object):
    def __init__(self, descriptor=None, gmm=None, pca=None, metric=None, do_weak_scale=False, do_random_jitter=False):
        if descriptor is None and gmm is not None and pca is not None and metric is not None:
            self.descriptor = CompactAndDiscriminativeFaceTrackDescriptor(gmm=gmm, pca=pca, metric=metric, do_weak_scale=do_weak_scale, do_random_jitter=do_random_jitter)
        elif descriptor is not None:
            self.descriptor=descriptor
        else:
            self.descriptor = load(os.path.join(strpy.bobo.app.models(), 'D0.2', 'cs2_split1_3Dv4b_CADFTD_23_JAN15.pk'))

    def encode(self, im):
        return self.descriptor.encode(im)

    def preprocess(self, im):
        return self.descriptor.preprocess(im)

    def train(self, trainset, gmmModes=512, pcaComponents=64, gmmIterations=20, do_ddr=True, do_jointmetric=True, do_parallel_sgd=False, seed=42, trainingFeatures=1E6, svmIterations=1E6, numBatches=1E2):
        return self.descriptor.train(trainset, gmmModes=gmmModes, pcaComponents=pcaComponents, gmmIterations=gmmIterations, do_ddr=do_ddr, do_jointmetric=do_jointmetric, do_parallel_sgd=do_parallel_sgd, seed=seed, trainingFeatures=trainingFeatures, svmIterations=svmIterations, numBatches=numBatches)

    def test(self, probeset=None, galleryset=None, with_templateid=False, with_labels=False):
        return self.descriptor.test(probeset, galleryset, with_templateid, with_labels)

    def augment_gallery(self, galleryset, rdd=True):
        return self.descriptor.augment_gallery(galleryset, rdd=rdd)


class RecognitionD0_2(object):
    def __init__(self, descriptor=None, gmm=None, pca=None, metric=None, do_weak_scale=False, do_random_jitter=False):
        if descriptor is None and gmm is not None and pca is not None and metric is not None:
            self.descriptor = CompactAndDiscriminativeFaceTrackDescriptor(gmm=gmm, pca=pca, metric=metric, do_weak_scale=do_weak_scale, do_random_jitter=do_random_jitter)
        elif descriptor is not None:
            self.descriptor = descriptor
        else:
            self.descriptor = load(os.path.join(strpy.bobo.app.models(), 'D0.2', 'cs2_split1_3Dv4b_CADFTD_23_JAN15.pk'))


    def frontalize(self, im, cache_root=strpy.bobo.app.janusCache(), gpu_idx=0, render_yaw_vals=[-40,0,40], render_pitch_vals=[-30,0,30]):
        images = []
        imorig = im.clone()
        sightingid = im.attributes['SIGHTING_ID'] if 'SIGHTING_ID' in im.attributes else 'null'
        chip_dir = os.path.join(strpy.bobo.app.janusCache(), 'pvr', 'chips')
        remkdir(chip_dir)
        chip_path = os.path.join(chip_dir, '%s.png' % sightingid)

        # Load frontlized chip from PVR output directory
        output_base_dir = cache_root + '/pvr/frontalized'
        frontalized_dir = output_base_dir + '/frontalized'

        # Write chip to file for PVR
        # PVR will resample small images with width < 250
        imorig = imorig.crop(bbox=imorig.bbox.dilate(1.1)).resize(cols=300)
        quietprint('[janus.recognition.frontalize]: Writing image chip to %s'%chip_path, 2)
        imorig.saveas(chip_path)

        try:
            # FIXME: Remove output files for repeated runs

            quietprint('[janus.recognition.frontalize]: Calling frontalization', 2)
            frontalize_face_v5(chip_path, gpu_idx=gpu_idx, cache_root=cache_root, render_yaw_vals=render_yaw_vals, render_pitch_vals=render_pitch_vals, subdir='20150707')

            glob_spec = frontalized_dir + '/%s_*_frontalized.png' % sightingid
            out_fnames = glob(glob_spec)
            # Make sure image order is stable
            out_fnames = sorted(out_fnames)

            quietprint('[janus.recognition.frontalize]: Found %d output files' % len(out_fnames), 2)

            # FIXME: SIGHTING_ID HACK for html viz
            for (k,fn) in enumerate(out_fnames, start=1):
                im = imorig.clone()
                im.data = imread(fn)
                im.bbox = BoundingBox(xmin=0, ymin=0, xmax=im.data.shape[1], ymax=im.data.shape[0])
                im.attributes['SIGHTING_ID'] = '%s_%d' % (sightingid, k)
                images.append(im)
                quietprint('[janus.recognition.frontalize]: Successfully read frontalized chip %s' % fn, 2)
        except IOError:
            print '[janus.recognition.frontalize]: Failed to frontalize image.  Returning original chip.'
            images.append(imorig)

        # make yaw/pitch look good in 3x3 arrangement
        if len(images) == 9:
            images = np.array(images)[[8,6,7,2,0,1,5,3,4]]
        elif len(images) > 0:
            images = np.array(images)[[0]]
        else:
            images = [imorig]
        return images

    def f_preprocess(self):
        return self.descriptor.f_preprocess()

    def preprocess(self, im):
        return self.descriptor.preprocess(im)

    def encode(self, im):
        return self.descriptor.encode(im)

    def train(self, trainset, gmmModes=512, pcaComponents=64, gmmIterations=20, do_ddr=True, do_jointmetric=True, do_parallel_sgd=False, seed=42, trainingFeatures=1E6, svmIterations=1E6, numBatches=1E2):
        return self.descriptor.train(trainset, gmmModes=gmmModes, pcaComponents=pcaComponents, gmmIterations=gmmIterations, do_ddr=do_ddr, do_jointmetric=do_jointmetric, do_parallel_sgd=do_parallel_sgd, seed=seed, trainingFeatures=trainingFeatures, svmIterations=svmIterations, numBatches=numBatches)

    def test(self, probeset=None, galleryset=None, with_templateid=False, with_labels=False):
        return self.descriptor.test(probeset, galleryset, with_templateid, with_labels)

    def augment_gallery(self, galleryset, rdd=True):
        return self.descriptor.augment_gallery(galleryset, rdd=rdd)

    def testfastpairs(self, rdd, pairs, isencoded=False):
        return self.descriptor.testfastpairs(rdd, pairs, isencoded=isencoded)


class RecognitionD1_0(object):

    def __init__(self, descriptor=None, gmm=None, pca=None, metric=None, do_weak_scale=False, do_random_jitter=False):
        if descriptor is None and gmm is not None and pca is not None and metric is not None:
            self.descriptor = CompactAndDiscriminativeFaceTrackDescriptor(gmm=gmm, pca=pca, metric=metric, do_weak_scale=do_weak_scale, do_random_jitter=do_random_jitter)
        elif descriptor is not None:
            self.descriptor = descriptor
        else:
            self.descriptor = load(os.path.join(strpy.bobo.app.models(), 'D0.2', 'cs2_split1_3Dv5_RecogD0.2_16FEB15.pk'))


    def frontalize(self, im, cache_root=strpy.bobo.app.janusCache(), gpu_idx=0, render_yaw_vals=[-40,0,40], render_pitch_vals=[-30,0,30]):
        images = []
        imorig = im.clone()
        sightingid = int(im.attributes['SIGHTING_ID']) if isinstance(im.attributes, dict) and 'SIGHTING_ID' in im.attributes else 0
        chip_dir = os.path.join(strpy.bobo.app.janusCache(), 'pvr', 'chips')
        remkdir(chip_dir)
        chip_path = os.path.join(chip_dir, '%08d.png' % sightingid)

        # Load frontlized chip from PVR output directory
        output_base_dir = cache_root + '/pvr/frontalized'
        frontalized_dir = output_base_dir + '/frontalized/20150707'

        # Write chip to file for PVR
        # PVR will resample small images with width < 250
        imorig = imorig.crop(bbox=imorig.bbox.dilate(2.0)).resize(cols=300) # make much bigger for context
        quietprint('[janus.recognition.frontalize]: Writing image chip to %s'%chip_path, 2)
        imorig.saveas(chip_path)

        try:
            glob_spec = frontalized_dir + '/%08d_*_frontalized.png' % sightingid
            out_fnames = glob(glob_spec)
            [os.remove(f) for f in out_fnames]  # remove previous run

            quietprint('[janus.recognition.frontalize]: Calling frontalization', 2)
            frontalize_face_v5(chip_path, gpu_idx=gpu_idx, cache_root=cache_root, render_yaw_vals=render_yaw_vals, render_pitch_vals=render_pitch_vals, subdir='20150707')

            # Make sure image order is stable
            glob_spec = frontalized_dir + '/%08d_*_frontalized.png' % sightingid
            out_fnames = glob(glob_spec)
            out_fnames = sorted(out_fnames)

            quietprint('[janus.recognition.frontalize]: Found %d output files' % len(out_fnames), 2)

            # FIXME: SIGHTING_ID HACK for html viz
            for (k,fn) in enumerate(out_fnames, start=1):
                im = imorig.clone().filename(fn)
                im.bbox = BoundingBox(xmin=0, ymin=0, xmax=im.width(), ymax=im.height())
                im.attributes['SIGHTING_ID'] = k
                images.append(im)
                quietprint('[janus.recognition.frontalize]: Successfully read frontalized chip %s' % fn, 2)
        except IOError as e:
            print '[janus.recognition.frontalize]: Failed to frontalize image.  Returning original chip.'
            print '[janus.recognition.frontalize]:', e

        # Augment template with original
        images.append(imorig)

        # make yaw/pitch look good in 3x3 arrangement
        if len(images) == 10:
            images = np.array(images)[[8,6,7,2,0,1,5,3,4,9]]
        elif len(images) > 0:
            images = np.array(images)[[0]]
        else:
            images = [imorig]

        return images


    def preprocess(self, im):
        return self.descriptor.preprocess(im)

    def train(self, trainset, gmmModes=512, pcaComponents=64, gmmIterations=20, do_metric=True, do_ddr=True, do_jointmetric=True, do_parallel_sgd=False, seed=42, trainingFeatures=1E6, numIterations=1E6, numBatches=1E2):
        self.descriptor.train(trainset, gmmModes=gmmModes, pcaComponents=pcaComponents, gmmIterations=gmmIterations, do_metric=do_metric, do_ddr=do_ddr, do_jointmetric=do_jointmetric, do_parallel_sgd=do_parallel_sgd, seed=seed, trainingFeatures=trainingFeatures, svmIterations=numIterations, numBatches=numBatches)
        return self

    def test(self, probeset=None, galleryset=None, with_templateid=False, with_labels=False):
        return self.descriptor.test(probeset, galleryset, with_templateid, with_labels)

    def testfast(self, probeset=None, galleryset=None):
        # FIXME: should this be self.descriptor.testfast?
        return self.descriptor.test(probeset, galleryset)

    def augment_gallery(self, galleryset, rdd=True):
        return self.descriptor.augment_gallery(galleryset, rdd=rdd)


class RecognitionD11(RecognitionD1_0):

    def __init__(self, descriptor=None, gmm=None, pca=None, metric=None):
        super(RecognitionD11, self).__init__(descriptor=descriptor, gmm=gmm, pca=pca, metric=metric)
        self.svm = None

    def _check_svm(self):
        if self.svm is None:
            if self.descriptor.pca is None or self.descriptor.gmm is None:
                raise ValueError, '[janus.recognition-1.1]: Model has not been trained1'
            self.svm = LinearSVMGalleryAdaptation(self.descriptor.f_encoding)

    def load(filename):
        ''' Construct a new instance of RecognitionD11 using an existing RecognitionD* instance.  This gets rid of stale code in un-pickled models.'''
        ref = bobo.util.load(filename)
        new = RecognitionD11(pca=ref.descriptor.pca, gmm=ref.descriptor.gmm, metric=ref.descriptor.metric)
        return new
    load = staticmethod(load)


    def encode(self, t):
        return self.descriptor.encode(t)


    def trainsvms(self, sparkContext, trainset, galleryset, use_gallery_negatives=True, class_method='svm'):
        self._check_svm()
        return self.svm.train(sparkContext=sparkContext, trainset=trainset, galleryset=galleryset, use_gallery_negatives=use_gallery_negatives, class_method=class_method)

    def testsvmsingle(self, probeset, galleryset, gallerysvms):
        self._check_svm()
        return self.svm.testsingle(probeset=probeset, galleryset=galleryset, gallerysvms=gallerysvms)

    def testsvm(self, sparkContext, probeset, galleryset, gallerysvms, probesvms):
        self._check_svm()
        return self.svm.test(sparkContext=sparkContext, probeset=probeset, galleryset=galleryset, gallerysvms=gallerysvms, probesvms=probesvms)



class RecognitionD20(object):

    def __init__(self, gpu=False, noweights=False,gpu_idx=0):
        # mean BGR pixel - from vgg_face.mat convNet.net.normalization.averageImage
        mean_pix = np.array([
            93.5940,  # B
            104.7624, # G
            129.1863, # R
            ])

        # Initialize our net
        from janus.network import CaffeNet
        model = os.path.join(janus.environ.models(), 'vgg', 'caffe_release_17SEP15', 'VGG_FACE_16_layers_deploy.prototxt')
        #print '[janus_demo_vgg_cnn] Using model prototxt: %s' % model
        weightsfile = None if noweights else os.path.join(janus.environ.models(), 'vgg', 'caffe_release_17SEP15', 'VGG_FACE_16_layers.caffemodel')
        #print '[janus_demo_vgg_cnn] Using model weights: %s' % weightsfile
        self.caffenet = CaffeNet(model=model, weights=weightsfile, use_gpu=gpu, batch_size=1, mean_pix=mean_pix,gpu_idx=gpu_idx)
        self.gallery = {'features':None, 'subjects':[]}

    def _encode(self, imset):
        if not islist(imset):
            return self.caffenet.encode(imset.crop(), layer_end='fc7')  # singleton
        else:
            return self.caffenet.encode([im.crop() for im in imset], layer_end='fc7')  # batch

    def _multiscale_encode(self, im):
        imset = []
        for s in [256,384,512]:  # 3x scales
            ims = im.clone().crop().resize(rows=s, cols=s)
            imscale = [ims.clone().boundingbox(xmin=0, ymin=0, xmax=224, ymax=224).crop(),  # upper left
                       ims.clone().boundingbox(xmin=s-224, ymin=0, width=224, height=224).crop(),  # upper right
                       ims.clone().boundingbox(xmin=0, ymin=s-224, width=224, height=224).crop(),  # lower left
                       ims.clone().boundingbox(xmin=s-224, ymin=s-224, width=224, height=224).crop(),  # lower right
                       ims.clone().boundingbox(xcentroid=s/2, ycentroid=s/2, width=224, height=224).crop()]  # center
            imset = imset + imscale + [im.clone().fliplr() for im in imscale] # corner crops, center crop, mirrors = 10 images per scale
        return self.caffenet.encode(imset, layer_end='fc7')  # batch
     #  encode media augmented with frontalized images
    def _multiscale_encode_media(self, media):
        imset = []
        for im in media:
        #     for s in [256,384,512]:  # 3x scales
        #         ims = im.clone().crop().resize(rows=s, cols=s)
        #         imscale = [ims.clone().boundingbox(xmin=0, ymin=0, xmax=224, ymax=224).crop(),  # upper left
        #                ims.clone().boundingbox(xmin=s-224, ymin=0, width=224, height=224).crop(),  # upper right
        #                ims.clone().boundingbox(xmin=0, ymin=s-224, width=224, height=224).crop(),  # lower left
        #                ims.clone().boundingbox(xmin=s-224, ymin=s-224, width=224, height=224).crop(),  # lower right
        #                ims.clone().boundingbox(xcentroid=s/2, ycentroid=s/2, width=224, height=224).crop()]  # center
        #         imset = imset + imscale + [im.clone().fliplr() for im in imscale]  # corner crops, center crop, mirrors = 10 images per scale
        # final_set = imset;
            imset += [im.clone().crop()]
        final_set =  imset +  [im.clone().fliplr() for im in imset]

        return self.caffenet.encode(final_set, layer_end='fc7')  # batch

    def getweights(self):
        return self.caffenet.getweights()

    def setweights(self, W):
        return self.caffenet.setweights(W)

    def setgallery(self, g):
        if isstring(g) and os.path.exists(g):
            self.gallery = load(g)
        return self

    def gallerysize(self):
        return len(self.gallery['subjects'])

    #  encode media augmented with frontalized images and return list of encodings
    def encode_media(self, media, multiscale=True):
        media = tolist(media)
        return self._encode(media) if not multiscale else self._multiscale_encode_media(media)

    def encode(self, im, multiscale=False, normalize=True):
        if im.mediatype() == 'image':
            v = self._encode(im).flatten() if not multiscale else self._multiscale_encode(im).flatten()
        elif im.mediatype() == 'video':
            v = np.mean(self._encode(im.frames()), axis=0).flatten()
        elif im.mediatype() == 'template':
            v = np.mean([self.encode(x, multiscale=multiscale, normalize=False).flatten() for x in im], axis=0).flatten()
        else:
            raise ValueError()
        return bobo.geometry.normalize(v) if normalize else v

    def enroll(self, m):
        x = bobo.linalg.rowvector(self.encode(m))
        self.gallery['features'] = np.vstack( (self.gallery['features'], x) ) if self.gallery['features'] is not None else x
        self.gallery['subjects'].append(m.clone().flush())
        return self

    def _rotationsearch(self, videofile, minDetrate):
        f_facedetector=DlibObjectDetector()
        rotations = [90, 0, 270] if fileext(videofile).lower() == '.mov' else [270, 0, 90]  # iphone .MOV == +90, android .mp4 == +270
        for r in rotations:
            v = VideoDetection(videofile=videofile, category='Face', rot90clockwise=(r==90), rot270clockwise=(r==270), framerate=1)
            v_det = v.clone()
            v_det = v_det.frames([im.boundingbox(bbox=bb[0]) for (im,bb) in [(im, f_facedetector(im)) for im in v_det] if len(bb)>0 and bb[0].isvalid()])
            detrate = float(len(v_det)) / float(len(v))
            if detrate > minDetrate:
                return r
        raise ValueError('No faces detected')

    def enrollvideo(self, videofile, subjectid, f_facedetector=None, rotate=None, framerate=2, minDetrate=0.1):
        """f_facedetector is callable, takes image objects and returns a list of boundingbox objects"""
        f_facedetector = DlibObjectDetector() if f_facedetector is None else f_facedetector
        rotate = self._rotationsearch(videofile, minDetrate=minDetrate) if rotate is None else rotate
        v = VideoDetection(videofile=videofile, category=subjectid, rot90clockwise=(rotate==90), rot270clockwise=(rotate==270), framerate=framerate)
        v_det = v.clone()
        v_det = v_det.frames([im.boundingbox(bbox=bb[0]) for (im,bb) in [(im, f_facedetector(im)) for im in v_det] if len(bb)>0 and bb[0].isvalid()])
        if (float(len(v_det)) / float(len(v))) > minDetrate:
            return self.enroll(v_det)
        else:
            print (float(len(v_det)) / float(len(v)))
            print minDetrate
            raise ValueError('No faces detected')

    def search(self, x, rank=1):
        if len(self.gallery['subjects']) > 0:
            d = sqdist(self.gallery['features'], bobo.linalg.rowvector(x)).flatten()
            k = np.argsort(d)  # increasing order
            S = self.gallery['subjects']
            result = [(S[j].category(), -float(d[j])) for j in k[0:rank]]
            return result if rank>1 else result[0]
        else:
            return None

    def identify(self, m):
        return self.search(self.encode(m), rank=1)[0]


class RecognitionD20_retrained(RecognitionD20):
    def __init__(self, prototxt, caffemodel, gpu=False, gpu_idx=0):
        # mean BGR pixel - from vgg_face.mat convNet.net.normalization.averageImage
        mean_pix = np.array([
            93.5940,  # B
            104.7624, # G
            129.1863, # R
            ])

        # Initialize our net
        from janus.network import CaffeNet
        model = prototxt
        print '[RecognitionD20_retrained] Using model prototxt: %s' % model
        weightsfile = caffemodel
        print '[RecognitionD20_retrained] Using model weightst: %s' % weightsfile
        self.caffenet = CaffeNet(model=model, weights=weightsfile, use_gpu=gpu, batch_size=1, mean_pix=mean_pix,gpu_idx=gpu_idx)
        self.gallery = {'features':None, 'subjects':[]}



# FIXME: Hack to workaround RecognitionD11 assumptions
class Dummy(object):
    def __init__(self, encoding):
        self.pca = 1
        self.gmm = 1
        self.f_encoding = encoding

class RecognitionD21(RecognitionD11):
    """D2.0 with gallery adaptation"""
    def __init__(self, gpu=False, noweights=False):
        super(RecognitionD11, self).__init__()
        self.svm = None
        self.descriptor = Dummy(self.encode)

        # mean BGR pixel - from vgg_face.mat convNet.net.normalization.averageImage
        self.mean_pix = np.array([
            93.5940,  # B
            104.7624, # G
            129.1863, # R
            ])

        # Initialize our net
        # from janus.network import CaffeNet
        self.model = os.path.join(janus.environ.models(), 'vgg', 'caffe_release_17SEP15', 'VGG_FACE_16_layers_deploy.prototxt')
        #print '[janus_demo_vgg_cnn] Using model prototxt: %s' % model
        self.weightsfile = None if noweights else os.path.join(janus.environ.models(), 'vgg', 'caffe_release_17SEP15', 'VGG_FACE_16_layers.caffemodel')
        #print '[janus_demo_vgg_cnn] Using model weights: %s' % weightsfile
        # self.caffenet = CaffeNet(model=model, weights=weightsfile, use_gpu=gpu, batch_size=1, mean_pix=mean_pix)
        self.caffenet = None
        self.use_gpu=gpu

    def setcaffe(self):
        from janus.network import CaffeNet
        if self.caffenet == None:
            self.caffenet = CaffeNet(model=self.model, weights=self.weightsfile, use_gpu=self.use_gpu, mean_pix=self.mean_pix)

    def _encode(self, imset):
        if len(imset) == 1:
            return self.caffenet.encode(imset.crop(), layer_end='fc7')  # singleton
        else:
            return self.caffenet.encode([im.crop() for im in imset], layer_end='fc7')  # batch

    def getweights(self):
        self.setcaffe()
        return self.caffenet.getweights()

    def setweights(self, W):
        self.setcaffe()
        return self.caffenet.setweights(W)

    def encode(self, im, normalize=True):
        self.setcaffe()
        # return np.random.rand(1,4096).astype(np.float32).flatten()
        if im.mediatype() == 'image':
            v = self._encode(im).flatten()
        elif im.mediatype() == 'video':
            v = np.mean(self._encode(im.frames()), axis=0).flatten()
        elif im.mediatype() == 'template':
            v = np.mean([self.encode(x, normalize=False).flatten() for x in im], axis=0).flatten()
        else:
            raise ValueError()
        return bobo.linalg.normalize(v) if normalize else v

    def encode_media(self, media, multiscale=True):
        media = tolist(media)
        return self._encode(media) if not multiscale else self._multiscale_encode(media)



class RecognitionD21b(RecognitionD20):
    """D2.0 with gallery and probe adaptation - Implemented in T&E wrapper"""



class RecognitionD30(object):
    """D3.0 with str-dlib network"""

    def __init__(self, modelfile, gpu=[0], encoder=None):
        self._model = os.path.join(janus.environ.models(), 'str-dlib', modelfile)
        if not os.path.exists(self._model):
            raise IOError('model "%s" not found' % self._model)
        self._gpu = tolist(gpu)

        if encoder is None:
            # If model is 'A_B_C.dlib', then exe is assumed to be 'A' or 'A_B' in same directory
            parts = filebase(self._model).split('_')
            if len(parts) >= 1 and os.path.exists(os.path.join(janus.environ.models(), 'str-dlib', parts[0])):
                self._encoder = os.path.join(janus.environ.models(), 'str-dlib', parts[0])
            elif len(parts) >= 2 and os.path.exists(os.path.join(janus.environ.models(), 'str-dlib', '%s_%s' % (parts[0], parts[1]))):
                self._encoder = os.path.join(janus.environ.models(), 'str-dlib', '%s_%s' % (parts[0], parts[1]))
            else:
                raise IOError('exectuable not found for model file "%s"' % modelfile)
        else:
            self._encoder = encoder

    def __repr__(self):
        return str('<RecognitionD3.0: exe="%s", model="%s", gpus="%s">' % (self._encoder, self._model, str(self._gpu)))


    def encode(self, imlist, mtxfile=None):
        outfile = mktemp('mtx') if mtxfile is None else mtxfile
        S = {s:k for (k,s) in enumerate(list(set([im.category() for im in imlist])))}  # subjects to ints
        csvfile = writecsv([(im.filename(), S[im.category()], round(im.boundingbox().xmin), round(im.boundingbox().ymin), round(im.boundingbox().width()), round(im.boundingbox().height())) for im in imlist], mktemp('csv'))
        cmd = '%s --gpuid=%d --gpu=%d --model=%s --encode=%s --mtx=%s' % (self._encoder, np.min(self._gpu), len(self._gpu), self._model, csvfile, outfile)
        if os.system(cmd) != 0:
            raise IOError('Error running "%s"' % cmd)
        if mtxfile is None:
            return readbinary(outfile)
        else:
            return outfile

    def encodecsv(self, csvfile, mtxfile, flags=None):
        prms = ' '.join(['--%s' % str(k) for k in flags.keys()]) if flags is not None else ''
        cmd = '%s --gpuid=%d --gpu=%d --model=%s --encode=%s --mtx=%s %s' % (self._encoder, np.min(self._gpu), len(self._gpu), self._model, csvfile, mtxfile, prms)
        print '[recognitiond30.encodecsv]: executing "%s"' % cmd
        if os.system(cmd) != 0:
            raise IOError('Error running "%s"' % cmd)
        return mtxfile


